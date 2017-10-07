import logging

from sanic import Sanic
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import beluga.config as config
from beluga.routes import api
from beluga.utils import parse_database_url

# Build app and configuration.
app = Sanic()
app.config.from_object(config)

logger = None

# Database setup.
engine = create_engine(app.config.DATABASE_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import beluga.models
    Base.metadata.create_all(bind=engine)


@app.middleware("request")
async def log_uri(request):
    # Simple middleware to log the URI endpoint that was called
    app.logger.info("URI called: {0}".format(request.url))


# Async approach.....
# @app.listener('before_server_start')
# async def before_server_start(app, loop):
#     app.logger.info("Initializing database.... ")
#     async with create_engine(connection) as engine:
#         init_db()


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.logger.info("Closing database pool")
    db_session.remove()


# Final configurations and logging.
logging.basicConfig(level=logging.DEBUG)
app.logger = logging.getLogger()
app.blueprint(api)
init_db()
