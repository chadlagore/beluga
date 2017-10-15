from contextlib import contextmanager
import logging

from sanic import Sanic
from sqlalchemy import create_engine

from beluga import config
from beluga.routes import api
from beluga.models import db_setup


# Build app and configuration.
app = Sanic()
app.config.from_object(config)

# Basic app level logging config.
logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger(__name__)


@app.middleware("request")
async def log_uri(request):
    # Simple middleware to log the URI endpoint that was called
    app.logger.info("URI called: {0}".format(request.url))


@app.listener('before_server_start')
async def setup_db(app, loop):
    db_setup()


app.blueprint(api)
app.logger.info("Routes initialized.")
