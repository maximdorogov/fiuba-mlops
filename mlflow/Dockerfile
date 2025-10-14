FROM python:3.12-slim

RUN apt-get update && apt-get install -y wget
RUN pip install --upgrade pip
RUN pip install mlflow[extras]

COPY mlflow/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

CMD [ "mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]