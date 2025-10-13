FROM python:3.11.0-slim

WORKDIR /app

#COPY ./Qwen2.5-VL-3B-Instruct ./Qwen2.5-VL-3B-Instruct

RUN pip install --upgrade pip

COPY ./inference_api/requirements.txt .
RUN pip install -r requirements.txt

COPY ./inference_api/src ./src
COPY ./inference_api/models ./models

ENTRYPOINT [ "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000" ]