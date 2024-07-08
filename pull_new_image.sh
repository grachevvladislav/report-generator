#!/bin/bash
docker compose stop
docker rm report-generator-bot
docker compose up -d
