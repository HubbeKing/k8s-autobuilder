FROM docker.io/library/python:3.9-slim

LABEL org.opencontainers.image.source = "https://github.com/HubbeKing/k8s-autobuilder"

RUN mkdir -p /app

ADD . /app

WORKDIR /app

RUN pip install .

CMD gunicorn -w 4 backend:app
