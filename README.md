beluga
===================

Event tracking, rating and prioritizing for your event going pleasure.


## :running: Getting Started

You will need Docker Compose(`pip uninstall docker-compose`).

```bash
docker-compose up
```

## :shipit: Deployment

The production `Dockerfile` gets pulled and built from the master
branch by DockerHub.

## :books: Docs

We use [ApiDoc](http://apidocjs.com/).

```bash
npm install apidoc -g
```

To generate the docs and view them:

```bash
apidoc -i beluga/ -o docs
python -m SimpleHTTPServer
```

Head to the `docs` folder.

## Testing

```bash
make test
```