#!/bin/bash

# For travis use only.
# Example usage: ./bin/deploy.sh heroku

TARGET=$1

set -e # Abort script at first error
set -u # Disallow unset variables

if [ "$TRAVIS_BRANCH" = "master" ]; then
    if [ "$TARGET" = "heroku" ]; then

        # Install the toolbelt, and the required plugin.
        wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
        heroku plugins:install heroku-docker
        heroku container:login

        # Heroku likes this approach.
        cp Dockerfile Dockerfile.web
        cp worker/Dockerfile Dockerfile.worker

        # Push all containers to registry
        heroku container:push web worker \
            --recursive --app "$PRODUCTION_APP"

    elif [ "$TARGET" = "gcp" ]; then
        echo "GCP deployment not implemented"
    else
        echo "Usage: ./deploy.sh [target]"
    fi;
fi;
