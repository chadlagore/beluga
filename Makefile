
.PHONY: all run-dev build

all: build

run-dev:
	docker-compose up

build:
	docker build --rm -t $(PROD_IMAGE_NAME) .

test:
	docker-compose run webdev pytest -vvv
