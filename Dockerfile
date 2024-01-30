FROM python:3.11-slim
RUN apt-get update && \
    apt-get install -y \
        locales && \
    rm -r /var/lib/apt/lists/*
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales
COPY src/ ./src
COPY files/ ./files
RUN pip3 install -r files/requirements.txt --no-cache-dir
CMD ["python", "./src/main.py" ]
