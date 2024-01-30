FROM python:3.11-slim
RUN apt-get install -y language-pack-ru
COPY src/ ./src
COPY files/ ./files
RUN pip3 install -r files/requirements.txt --no-cache-dir
CMD ["python", "./src/main.py" ]
