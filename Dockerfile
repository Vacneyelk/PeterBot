FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get -y install git

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ADD bot /app/bot

WORKDIR /app/bot

CMD [ "python3", "-u", "launcher.py" ]