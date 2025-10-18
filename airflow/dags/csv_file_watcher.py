from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import os
import pandas as pd


MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://s3:9000")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "csv-data")
INCOMING_PREFIX = "incoming/"
PROCESSED_PREFIX = "processed/"

def clean_data(df: pd.DataFrame, expected_columns: set) -> pd.DataFrame:
    """
    Clean the input DataFrame by removing NaNs and keeping only expected 
    columns.

    Parameters
    ----------
    df: pd.DataFrame
        The input DataFrame to clean.
    expected_columns: set
        A set of expected column names to retain in the DataFrame.

    Returns
    -------
    pd.DataFrame
        The cleaned DataFrame.
    """

    df.dropna(inplace=True)
    if len(expected_columns) != 0:
        df = df[[col for col in df.columns if col in expected_columns]]
    return df


def process_specific_csv_file(**context):
    """
    Process a specific CSV file that was detected by the sensor.
    This version gets the file path from the sensor's return value.
    """
    # Get the file path from the sensor task
    ti = context['ti']
    file_key = ti.xcom_pull(task_ids='wait_for_new_csv')

    print(f"XCom value from sensor: {file_key}")
    print(f"XCom type: {type(file_key)}")

    # Initialize S3 client for file operations
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-1",
    )

    # If sensor didn't return a specific file, find any CSV file in incoming folder
    if not file_key or file_key is True:
        # List all files in incoming folder
        try:
            response = s3.list_objects_v2(Bucket=MINIO_BUCKET, Prefix=INCOMING_PREFIX)
            csv_files = [obj['Key'] for obj in response.get('Contents', []) 
                        if obj['Key'].endswith('.csv') and obj['Key'] != INCOMING_PREFIX]

            if csv_files:
                file_key = csv_files[0]  # Process the first CSV file found
                print(f"Found CSV file to process: {file_key}")
            else:
                print("✅ No CSV files found in incoming folder - nothing to process")
                print("This is normal behavior when no new files are available")
                return "No files to process"
        except Exception as e:
            print(f"Error listing files: {e}")
            return

    print(f"Processing file: {file_key}")

    filename = file_key.split("/")[-1]
    tmp_path = f"/tmp/{filename}"

    try:
        print(f"📥 Downloading: {file_key}")
        s3.download_file(MINIO_BUCKET, file_key, tmp_path)

        # Process the CSV
        df = pd.read_csv(tmp_path)
        df = clean_data(
            df,
            expected_columns={
                'airtemperature_k', 
                'process_temperature_k', 
                'rotational_speed_rpm', 
                'torque_nm', 
                'tool_wear_min', 
                'type_l', 
                'type_m', 
                'target'
            })

        df.to_csv(tmp_path, index=False)
        print(f"✅ Processed CSV saved to: {tmp_path}")

        # Upload the processed file back to MinIO
        print(f"📤 Uploading processed file to: {PROCESSED_PREFIX}{filename}")
        s3.upload_file(tmp_path, MINIO_BUCKET, f"{PROCESSED_PREFIX}{filename}")
        print(f"✅ Uploaded processed file to: {PROCESSED_PREFIX}{filename}")

        # delete the temporary local file
        os.remove(tmp_path)
        print(f"🧹 Removed temporary file: {tmp_path}")

        # delete the original file from incoming/
        print(f"🗑 Deleting original file from incoming/: {file_key}")
        s3.delete_object(Bucket=MINIO_BUCKET, Key=file_key)
        print(f"✅ Deleted original file: {file_key}")

        # Move file to processed/
        new_key = f"{PROCESSED_PREFIX}{filename}"
        print(f"📦 Moving {file_key} → {new_key}")
        s3.copy_object(
            Bucket=MINIO_BUCKET,
            CopySource={"Bucket": MINIO_BUCKET, "Key": file_key},
            Key=new_key,
        )
        s3.delete_object(Bucket=MINIO_BUCKET, Key=file_key)
        print(f"🧹 Cleaned up source file: {file_key}")

    except Exception as e:
        print(f"❌ Error processing file {file_key}: {str(e)}")
        raise

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# DAG that continuously waits for new files using S3KeySensor
with DAG(
    dag_id="minio_csv_file_watcher",
    start_date=datetime(2024, 1, 1),
    schedule_interval=timedelta(minutes=2),  # Check every 2 minutes for new files
    catchup=False,
    default_args=default_args,
    tags=["minio", "csv", "file-watcher", "auto-trigger"],
    max_active_runs=1,  # Prevent multiple instances running simultaneously
    is_paused_upon_creation=False,  # Start unpaused automatically
) as dag:

    wait_for_new_csv = S3KeySensor(
        task_id="wait_for_new_csv",
        bucket_key=f"{INCOMING_PREFIX}*.csv",  
        bucket_name=MINIO_BUCKET,
        wildcard_match=True,
        poke_interval=30,  # Check every 30 seconds for files  
        timeout=90,       # Timeout after 90 seconds (less than 2 min schedule)
        mode='reschedule', # Use reschedule mode (more efficient)
        aws_conn_id="minio_conn",
        soft_fail=True,   # Don't fail the DAG run when no file found
    )

    process_csv_file = PythonOperator(
        task_id="process_csv_file",
        python_callable=process_specific_csv_file,
    )
    # Tell dag to run processing after file detection
    wait_for_new_csv >> process_csv_file