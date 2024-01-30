FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    locales && \
    rm -r /var/lib/apt/lists/*
COPY src/ ./src
COPY files/ ./files
RUN pip3 install -r files/requirements.txt --no-cache-dir
CMD ["python", "./src/main.py" ]
