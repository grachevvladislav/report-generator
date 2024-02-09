#!/bin/bash
docker compose stop
docker rm report-generator-bot
docker pull grachevvladislav/report-generator:latest
docker compose up -d
