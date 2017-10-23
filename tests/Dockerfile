FROM python:3.6-stretch

# Install production dependencies.
COPY requirements.txt /env/requirements.txt
COPY worker/requirements.txt /env/requirements-worker.txt
COPY tests/requirements.txt /env/requirements-test.txt
RUN pip install -r /env/requirements.txt
RUN pip install -r /env/requirements-worker.txt
RUN pip install -r /env/requirements-test.txt

# Add application to container.
COPY . /app/

WORKDIR /app/

CMD pytest -vvv
