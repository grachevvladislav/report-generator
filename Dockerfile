FROM python:3.11-slim
COPY src/ files/ .
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["python", "src/main.py" ]
