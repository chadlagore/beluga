TARGET=$1

if [ "$TARGET" = "heroku" ]; then
    cp Dockerfile Dockerfile.web
    cp worker/Dockerfile Dockerfile.worker
    heroku container:push web worker --recursive
    rm Dockerfile.web
    rm Dockerfile.worker
elif [ "$TARGET" = "gcp" ]; then
    echo "GCP deployment not implemented"
else
    echo "Usage: ./deploy.sh [target]"
fi;
