# # pull official base image
FROM python:3.9.5-slim-buster as builder
RUN mkdir /usr/src/app/

# # set work directory
WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY . /usr/src/app/

# # install python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
