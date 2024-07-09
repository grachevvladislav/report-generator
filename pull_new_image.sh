#!/bin/bash
docker compose stop
docker compose down
docker rm report-generator-bot
docker compose up -d --build
docker exec -it report-generator-django bash
python manage.py migrate
