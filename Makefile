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

.PHONY: all run-dev run-prod build-prod

all: build-prod

run-dev:
	docker rm -f $(PROD_CONTAINER) 2>> /dev/null || true
	docker run -it \
		--name $(PROD_IMAGE_NAME) \
		--env-file ./.env \
		-v `pwd`:/app \
		-p $(DEV_PORT):$(DEV_PORT) \
		$(PROD_IMAGE_NAME)

run-prod:
	docker rm -f $(PROD_CONTAINER) 2>> /dev/null || true
	docker run -it \
		--name $(PROD_IMAGE_NAME) \
		-e PROD=1 \
		-v `pwd`:/app \
		-p $(PROD_PORT):$(PROD_PORT) \
		$(PROD_IMAGE_NAME)

build-prod:
	docker build --rm -t $(PROD_IMAGE_NAME) .

test:
	# Swap image if we put dev image back in.
	docker run \
		-v `pwd`:/app \
		$(PROD_IMAGE_NAME) pytest -v
