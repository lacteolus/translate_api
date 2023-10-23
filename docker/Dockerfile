FROM python:3.10-alpine

WORKDIR /app

RUN mkdir app config

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app/* ./app

COPY config/* ./config

RUN mkdir -p ./log

ENV PYTHONPATH "${PYTHONPATH}:/app"