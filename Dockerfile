FROM python:3.8.10

ENV PYTHONUNBUFFERED=1

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY ./app /app

EXPOSE 8000