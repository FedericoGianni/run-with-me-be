# # pull official base image
FROM python:3.9.5-slim-buster as builder

# env to see python output on docker log
ENV FLASK_ENV="${FLASK_ENV}" \
    PYTHONUNBUFFERED=1

RUN mkdir /usr/src/app/

# # set work directory
WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY . /usr/src/app/

# # install python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
