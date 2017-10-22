FROM python:3.6-stretch

# Install production dependencies.
ADD requirements.txt /env/requirements.txt
ADD worker/requirements.txt /env/requirements-worker.txt
ADD tests/requirements.txt /env/requirements-test.txt
RUN pip install -r /env/requirements.txt
RUN pip install -r /env/requirements-worker.txt
RUN pip install -r /env/requirements-test.txt

# Add application to container.
ADD . /app/

WORKDIR /app/

CMD pytest -vvv
