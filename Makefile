
.PHONY: all run-dev build

all: build

dev:
	docker-compose up

test:
	docker-compose run webdev pytest -vvv
