FROM python:3.6.2-slim

# Install production dependencies.
ADD requirements.txt /env/requirements.txt
RUN pip install -r /env/requirements.txt

# Add application to container.
ADD impala_beluga /app/impala_beluga/

WORKDIR /app/

ENTRYPOINT [ "python3" ]

CMD [ "impala_beluga/app.py" ]