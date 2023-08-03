# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
#COPY . .
RUN apt-get update && apt-get install -y make
RUN pip3 install scikit-learn numpy mlflow prefect notebook evidently black pylint pytest
