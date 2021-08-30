FROM docker.io/library/python:3.9-slim

RUN mkdir -p /app

ADD . /app

WORKDIR /app

RUN pip install .

CMD gunicorn -w 4 backend:app
