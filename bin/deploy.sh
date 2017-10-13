#!/bin/bash

# This is the deploy target.
TARGET=$1

set -e # Abort script at first error
set -u # Disallow unset variables

if [ "$TARGET" = "heroku" ]; then

    # Install the toolbelt, and the required plugin.
    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
    heroku plugins:install heroku-docker

    # Heroku likes this approach.
    cp Dockerfile Dockerfile.web
    cp worker/Dockerfile Dockerfile.worker

    # Push all containers to registry
    heroku container:push web worker --recursive

elif [ "$TARGET" = "gcp" ]; then
    echo "GCP deployment not implemented"
else
    echo "Usage: ./deploy.sh [target]"
fi;
