# syntax=docker/dockerfile:1.0.0-experimental
FROM ubuntu:18.04
FROM python:3.6

# Set Enviroment Variable
ENV PYTHONUNBUFFERED 1

# Make resource directory
RUN mkdir /ocr_worker

# Create work directory
WORKDIR /ocr_worker

# Update pip
RUN pip install --upgrade pip

# Installing requirements.pip from project
COPY ./ocr_worker/requirements.pip /scripts/
RUN pip install --no-cache-dir -r /scripts/requirements.pip

# Installing layout model
RUN apt-get -yq update
RUN apt-get -yqq install ssh
RUN apt-get install git
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh pip install lib-ocr[onmt,jeff]@git+ssh://git@github.com/Cinnamon/lib-ocr.git@master

# Get model weight
RUN mkdir /model
COPY ./ocr_worker/Model /model/

# CMD will run when this dockerfile is running
CMD ["sh", "-c", "gunicorn ocr_worker.wsgi -b 0.0.0.0:8001"]