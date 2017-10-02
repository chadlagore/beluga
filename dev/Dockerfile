FROM impala-beluga-prod:latest

# Install production dependencies.
ADD requirements.txt /env/requirements-dev.txt
RUN pip install -r /env/requirements-dev.txt

# Add everything to container.
ADD . /app/

ENTRYPOINT [ "/bin/bash" ]