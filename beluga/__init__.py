import logging

from sanic import Sanic
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import beluga.config as config
from beluga.routes import api

# Build app and configuration.
app = Sanic()
app.config.from_object(config)

# Basic logging config.
logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger(__name__)

# Database setup.
engine = create_engine(app.config.DATABASE_URL,
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


@app.middleware("request")
async def log_uri(request):
    # Simple middleware to log the URI endpoint that was called
    app.logger.info("URI called: {0}".format(request.url))


# Async approach.....
@app.listener('before_server_start')
async def before_server_start(app, loop):
    app.logger.info("Initializing database.... ")
    import beluga.models
    Base.metadata.create_all(bind=engine)
    app.logger.info("Database up.")


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.logger.info("Closing database pool")
    db_session.remove()

app.logger.info("Initializing routes")
app.blueprint(api)
