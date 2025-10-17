FROM apache/airflow:2.10.1

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         git \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
COPY ./airflow/requirements.txt ./requirements.txt

# Fix Python compatibility issues
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade setuptools>=68.0.0 wheel

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./airflow/dags /opt/airflow/dags
