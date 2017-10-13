#!/bin/bash

# For local use only.
# Example usage: ./bin/push-docs.sh

TARGET=$1

# Push docs to GCP.
if [ "$TARGET" = "gcp" ]; then
    apidoc -i beluga/ -o docs
    gsutil -m rsync -R docs gs://beluga-docs/api
    gsutil -m acl -r ch -u AllUsers:R gs://beluga-docs/api
else
    echo "Usage: ./deploy.sh [target]"
fi;
