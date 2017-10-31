FROM beluga_webdev

# Install production dependencies.
ADD worker/requirements.txt /env/requirements-worker.txt
ADD tests/requirements.txt /env/requirements-test.txt
RUN pip install -r /env/requirements-worker.txt
RUN pip install -r /env/requirements-test.txt

# Add application to container.
ADD . /app/

WORKDIR /app/

CMD pytest -vvv
