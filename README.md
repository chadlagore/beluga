beluga
===================

Event tracking, rating and prioritizing for your event going pleasure.


## :running: Getting Started

You will need [Docker](https://docs.docker.com/docker-for-mac/install/).

```bash
make        # Build containers.
make run    # Start server.
```

## :construction_worker: Development

Development dependencies are a superset of the production dependencies.
As such, the development container is inherited from the production 
container.

```bash
make dev    # Enter dev container and mount this repository.
```

## :shipit: Deployment


The production `Dockerfile` gets pulled and built from the master
branch by DockerHub.


## :books: Docs

```bash
npm install apidoc -g
apidoc -i beluga/ -o docs
python -m SimpleHTTPServer
```
