FROM beluga_webdev

# Install production dependencies.
ADD worker/requirements.txt /env/requirements-worker.txt
ADD tests/requirements.txt /env/requirements-test.txt
RUN pip install -r /env/requirements-worker.txt
RUN pip install -r /env/requirements-test.txt

# Add application to container.
ADD . /app/

WORKDIR /app/

ENV BELUGA_TEST true
ENV SECRET_BASE f5a9149cf77a47ddcc053a7731ec333a17b62238ff147345289a2d17fbd01eaec56946b5e339195484eb63140042e75c6ced01f46e196883eaee477240c46cdd

CMD pytest -vvv
