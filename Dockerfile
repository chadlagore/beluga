FROM python:3.6-stretch

# Install production dependencies.
ADD requirements.txt /env/requirements.txt
RUN pip install -r /env/requirements.txt

# Add application to container.
ADD beluga /app/beluga/

WORKDIR /app/

ENTRYPOINT [ "python3" ]

CMD [ "beluga/app.py" ]
