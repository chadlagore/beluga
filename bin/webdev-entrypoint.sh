#!/bin/bash
# Script stalls dev container until db comes up.

RET=1
echo "Waiting for database"
while ! pg_isready -h postgres -d beluga -U beluga; do
    sleep 10;
    echo "DB Not yet up."
done

# Boot app for development.
gunicorn --reload \
    --bind \
    0.0.0.0:8080 \
    --worker-class \
    sanic_gunicorn.Worker \
    beluga:app