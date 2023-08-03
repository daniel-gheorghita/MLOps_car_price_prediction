#!/bin/sh
docker build . -t mlops_car_price
docker-compose up -d
