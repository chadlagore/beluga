# Image names
PROD_IMAGE_NAME=beluga-prod
ORGANIZATION=chadlagore
TAG=latest

# Finding containers.
PROD_CONTAINER=`docker ps -aq --filter name=$(PROD_IMAGE_NAME)`

# Repository information.
PROD_LOCAL=$(PROD_IMAGE_NAME):$(TAG)
PROD_REMOTE=$(ORGANIZATION)/$(PROD_LOCAL)

# Ports
PROD_PORT=80
DEV_PORT=8080

.PHONY: all run build-prod

all: build-prod

run:
	docker rm -f $(PROD_CONTAINER) 2>> /dev/null || true
	docker run -it \
		--name $(PROD_IMAGE_NAME) \
		-v `pwd`/beluga:/app/beluga \
		-p $(PROD_PORT):$(PROD_PORT) \
		$(PROD_IMAGE_NAME)

build-prod:
	docker build --rm -t $(PROD_IMAGE_NAME) .
