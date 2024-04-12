FROM python:3.12-slim
RUN apt-get update && \
    apt-get install -y \
        locales && \
    rm -r /var/lib/apt/lists/*
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
WORKDIR /app
COPY backend/bot/ /app/backend
COPY files/ /app/files
RUN pip3 install -r /app/files/requirements.txt --no-cache-dir
