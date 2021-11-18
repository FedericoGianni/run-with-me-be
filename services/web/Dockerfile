# pull official base image
FROM python:3.9.5-slim-buster

RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
EXPOSE 5005
RUN pip install -r requirements.txt
CMD ["python3", "Api.py", "--host=0.0.0.0:5005"]
