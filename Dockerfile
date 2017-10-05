FROM python:3.6.2-jessie

# Install production dependencies.
ADD requirements.txt /env/requirements.txt
RUN pip install -r /env/requirements.txt

# Add application to container.
ADD . /app/

WORKDIR /app/

# Hot reload on app from code modifications.
CMD gunicorn \
    --reload \
    --bind 0.0.0.0:80 \
    --workers 4 \
    --worker-class \
    sanic_gunicorn.Worker \
    beluga:app
