FROM continuumio/miniconda3:latest

RUN pip install --upgrade pip mlflow

EXPOSE 5000

RUN mkdir -p /mlflow/db
RUN mkdir -p /mlflow/artifacts

#CMD mlflow server \
#    --backend-store-uri /mlflow-data \
#    --host 0.0.0.0 \
#    --default-artifact-root /mlflow-data


