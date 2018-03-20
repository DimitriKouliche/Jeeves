FROM python:3.6

MAINTAINER saufis

RUN mkdir /app

COPY Pipfile Pipfile.lock /app/

RUN pip install --upgrade pipenv && \
    cd /app/ && \
    pipenv install --deploy --system

RUN python -m nltk.downloader all

COPY . /app/

WORKDIR /app
