FROM python:3.10-bullseye
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt update && apt install libpq-dev -y
WORKDIR /code
RUN pip install --upgrade pip
COPY prod.requirements.txt /code/
RUN pip install -r prod.requirements.txt
COPY . /code/
RUN chmod +x celery.sh

COPY cron_job.sh /etc/periodic/15min
RUN chmod +x /etc/periodic/15min/cron_job.sh
