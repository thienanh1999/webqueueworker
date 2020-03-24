# syntax=docker/dockerfile:1.0.0-experimental
FROM ubuntu:18.04
FROM python:3.6

# Set Enviroment Variable
ENV PYTHONUNBUFFERED 1

# Make resource directory
RUN mkdir /webservice

# Create work directory
WORKDIR /webservice

# Update pip
RUN pip install --upgrade pip

# Installing requirements.pip from project
COPY ./webservice/requirements.pip /scripts/
RUN pip install --no-cache-dir -r /scripts/requirements.pip

# Installing layout model
RUN apt-get -yq update
RUN apt-get -yqq install ssh
RUN apt-get install git
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts
RUN --mount=type=ssh pip install lib-layout[tadashi]@git+ssh://git@github.com/Cinnamon/lib-layout.git@master --find-links https://download.pytorch.org/whl/torch_stable.html

# Get model weight
RUN mkdir /model
COPY ./webservice/Model /model/

# CMD will run when this dockerfile is running
CMD ["sh", "-c", "python manage.py collectstatic --no-input; python manage.py migrate; gunicorn webservice.wsgi -b 0.0.0.0:8000 & celery worker --app=webservice.tasks"]