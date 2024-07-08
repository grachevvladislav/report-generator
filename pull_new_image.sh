#!/bin/bash
docker compose stop
docker compose down
docker rm report-generator-bot
docker compose up -d --build
