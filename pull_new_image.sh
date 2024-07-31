#!/bin/bash
git pull
docker compose stop
docker compose down
docker compose up -d --build
docker exec -it report-generator-django sh -c "python manage.py migrate"
