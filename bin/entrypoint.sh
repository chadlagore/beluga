#!/usr/bin/env bash

if [ "$PROD" = "1" ]; then
    echo "Running for production."
    gunicorn \
        --bind 0.0.0.0:80 \
        --workers 4 \
        --worker-class sanic_gunicorn.Worker \
        beluga:app
else
    echo "Running for development."
    gunicorn \
        --reload \
        --bind 0.0.0.0:8080 \
        --worker-class sanic_gunicorn.Worker \
        beluga:app
fi;
