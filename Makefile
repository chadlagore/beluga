# Image names
PROD_IMAGE_NAME=beluga
DEV_IMAGE_NAME=beluga-dev
ORGANIZATION=chadlagore
TAG=latest

# Finding containers.
DEV_CONTAINER=`docker ps -aq --filter name=$(DEV_IMAGE_NAME)`
PROD_CONTAINER=`docker ps -aq --filter name=$(PROD_IMAGE_NAME)`

# Repository information.
DEV_LOCAL=$(DEV_IMAGE_NAME):$(TAG)
PROD_LOCAL=$(PROD_IMAGE_NAME):$(TAG)

# Ports
PROD_PORT=80
DEV_PORT=8080

.PHONY: all dev run build-prod build-dev push-dev

all: build-prod build-dev

run:
	docker rm -f $(PROD_CONTAINER) 2>> /dev/null || true
	docker run -it \
		--name $(PROD_IMAGE_NAME) \
		-v `pwd`/beluga:/app/beluga \
		-p $(PROD_PORT):$(PROD_PORT) \
		$(PROD_IMAGE_NAME)

dev:
	docker rm -f $(DEV_CONTAINER) 2>> /dev/null || true
	docker run -it \
		--name $(DEV_IMAGE_NAME) \
		-v `pwd`:/app \
		-p $(DEV_PORT):$(DEV_PORT) \
		$(DEV_IMAGE_NAME)

build-prod:
	docker build --rm -t $(PROD_IMAGE_NAME) .

build-dev:
	docker build --rm \
		-f ./dev/Dockerfile \
		-t $(DEV_IMAGE_NAME) .
