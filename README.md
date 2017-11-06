beluga
===================

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/94890da29c40447bb95c93a5bb680e56)](https://www.codacy.com/app/chad.d.lagore/beluga?utm_source=github.com&utm_medium=referral&utm_content=chadlagore/beluga&utm_campaign=badger)

[![Coverage Status](https://coveralls.io/repos/github/chadlagore/beluga/badge.svg?branch=master)](https://coveralls.io/github/chadlagore/beluga?branch=master)

Event tracking, rating and prioritizing for your event going pleasure.


## :running: Getting Started

You will need Docker Compose (`pip install docker-compose`).

```bash
docker-compose up  # Or docker-compose start for background.
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

We use a separate image to run our tests (see 
`tests/Dockerfile`). It still uses the `docker-compose` pattern,
because we would like for it to access postgres and redis etc.

```bash
docker-compose run test pytest -vvv
```

It will not run during a call to `docker-compose up`.
