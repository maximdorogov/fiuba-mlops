# Trabajo Practico final de la asignatura Operaciones de Aprendizaje Automatico

### Alumno: Maxim Dorogov

referencia: https://github.com/facundolucianna/amq2-service-ml/


## Descripcion del proyecto

Este proyecto implementa un sistema para la predicción de fallas en máquinas usando algoritmos de Support Vector Machine (SVM). La solución incluye el entrenamiento y registro de modelos en MlFlow, la implementación de una API para inferencia, despliegue y persistencia del modelo y su metadata (archivo serializado y métricas) y un sistema de orquestación para la ingesta y procesamiento de datos mediante Apache Airflow. La persistencia de datos se realiza utilizando bases de datos y buckets de AWS S3 (MinIO).

## Estructura del proyecto y componentes principales:

### **notebooks/**

    Notebook Jupyter (`notebooks/experiment.ipynb`) para experimentación con modelos de machine learning. En esta notebook se realizan las siguientes tareas:

    - Preprocesamiento de datos con pipelines de scikit-learn
    - Entrenamiento de modelos SVM para clasificación de fallas en máquinas
    - Búsqueda de hiperparámetros usando GridSearchCV
    - Evaluacion y registro de modelos y experimentos en MLflow.

### **mlflow/**
    - Servicio de MLflow para tracking y gestión de modelos.

### **inference_api/**

    La api fue desarrollada con FastAPI y esta compuesta por un endpoint de inferencia para predicción de fallas en máquinas y un endpoint de health check. Durante el proceso de inicialización, se intenta cargar el modelo "champion" desde el MLflow Model Registry. Si la conexión falla, o el modelo es inexistente, utiliza un modelo local como respaldo.

    ### Endpoints

    - `/predict`: El endpoint acepta un JSON con las características de funcionamiento de la máquina y devuelve una predicción indicando si se espera una falla o no.
    - `/`: Devuelve un JSON con el estado de la API.

### **airflow/**

    Sistema de orquestación de flujos de trabajo usando Apache Airflow. El DAG definido en `airflow/dags/csv_file_watcher.py.py` realiza las siguientes tareas:

    - Monitorea el bucket `csv-data/incoming/` a la espera de nuevos archivos CSV con datos de mediciones.
    - Procesa los archivos nuevos, aplicando transformaciones y limpieza de datos.
    - Mueve los archivos procesados a un nuevo bucket `csv-data/processed/`.

Funcionamiento del DAG:

- Paso 1: Nuevo archivo agregado a `csv-data/incoming/`
```sh
csv-data/
├── incoming/
│   └── measurements_2025_10_14.csv   ← agregado externamente
└── processed/
                                      ← vacio inicialmente
```
- Paso 2: Archivo procesado y movido a `csv-data/processed/`
```sh
csv-data/
├── incoming/
│                                     ← queda vacio despues del procesamiento
└── processed/
    └── measurements_2025_10_14.csv   ← movido por el dag al finalizar el procesamiento
```

## Requisitos del sistema
- Ubuntu 22.04.5 LTS
- Docker Engine v27.3.1
- Docker Compose v2.29.7
>NOTA: El proyecto podria funcionar en otros sistemas basados en Linux y versiones anteriores de docker y docker compose.

## Setup

Ejecutar desde la raiz del proyecto:

```sh
docker compose -f docker-compose.yml up --build
```

