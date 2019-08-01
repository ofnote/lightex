FROM continuumio/miniconda3:latest

RUN apt-get update && \
      apt-get -y --allow-unauthenticated install sudo

RUN pip install --upgrade pip jinja2 mlflow

EXPOSE 5000

ARG MLDATA
ARG LTEX
ARG GID
ARG UID


CMD echo "base dir = $LTEX $GID" \
    && groupadd --gid $GID ubuntu\
    && useradd -rm -d /home/ubuntu -s /bin/bash  ubuntu -u $UID -g $GID\
    && echo "ubuntu ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    && chown -R $UID:$GID $LTEX \
    && su - ubuntu \
    && mkdir -p $MLDATA \
    && ls -ld $LTEX \ 
    && mlflow server --backend-store-uri $MLDATA --host 0.0.0.0 --default-artifact-root $MLDATA



