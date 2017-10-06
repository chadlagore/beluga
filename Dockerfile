FROM python:3.6-stretch

# Install production dependencies.
ADD requirements.txt /env/requirements.txt
RUN pip install -r /env/requirements.txt

# Add application to container.
ADD . /app/

WORKDIR /app/

# Entrypoint tests for production.
CMD /app/bin/entrypoint.sh
