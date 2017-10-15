#!/bin/bash

# For travis/local use.
# Example usage: ./bin/deploy.sh heroku

TARGET=$1

set -e # Abort script at first error
set -u # Disallow unset variables

if [ "$TARGET" = "heroku" ]; then

    # Install the toolbelt, and the required plugin.
    # trues are so you can run this locally (you may
    # already have the deps).
    wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh || true
    heroku plugins:install heroku-docker || true
    heroku container:login

    # Push all containers to registry
    heroku container:push web worker \
        --recursive --app "$PRODUCTION_APP"

elif [ "$TARGET" = "gcp" ]; then
    echo "GCP deployment not implemented"
    exit 1
else
    echo "Usage: ./deploy.sh [target]"
fi;
