FROM python:3.9.13

WORKDIR /code

COPY requirements.txt /code

RUN pip3 install -r /code/requirements.txt

COPY . /code
