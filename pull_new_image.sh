#!/bin/bash
git pull
docker compose stop
docker compose down
yes Y | docker system prune -a
docker compose up -d
docker exec -it report-generator-django sh -c "python manage.py collectstatic --no-input"
docker exec -it report-generator-django sh -c "python manage.py migrate"
