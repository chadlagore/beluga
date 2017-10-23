#!/bin/bash
# Script stalls dev container until db comes up.

RET=1
echo "Waiting for database"
while ! pg_isready -h postgres -d beluga -U beluga; do
    sleep 10;
    echo "DB Not yet up."
done

# Run tests.
pytest -vvv