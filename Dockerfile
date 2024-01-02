FROM python:3.11-slim
WORKDIR /src
WORKDIR /files
COPY ["src/ ./src/", "files/ ./files/"]
RUN pip3 install -r files/requirements.txt --no-cache-dir
CMD ["python", "./src/main.py" ]
