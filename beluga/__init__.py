import logging

from sanic import Sanic
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from beluga import config
from beluga.routes import api

# Build app and configuration.
app = Sanic()
app.config.from_object(config)

# Basic logging config.
logging.basicConfig(level=logging.INFO)
app.logger = logging.getLogger(__name__)


def get_db_session():
    engine = create_engine(
            app.config.DATABASE_URL,
            convert_unicode=True)
    return engine, scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )


# Database tables.
_, db_session = get_db_session()
Base = declarative_base()
Base.query = db_session.query_property()


@app.middleware("request")
async def log_uri(request):
    # Simple middleware to log the URI endpoint that was called
    app.logger.info("URI called: {0}".format(request.url))


@app.listener('before_server_start')
async def before_server_start(app, loop):
    app.logger.info("Standing tables")
    engine, _ = get_db_session()
    import beluga.models  # noqa
    Base.metadata.create_all(bind=engine)
    app.logger.info("Initializing routes")


app.blueprint(api)
app.logger.info("Server configuration complete.")
