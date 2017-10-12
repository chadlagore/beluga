FROM python:3.6-stretch

# Install production dependencies.
ADD worker/requirements.txt /env/requirements.txt
RUN pip install -r /env/requirements.txt

# Add application to container.
ADD worker/ /app/
ADD beluga/ /app/

WORKDIR /app/
