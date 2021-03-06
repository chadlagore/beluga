import logging
import os

from contextlib import contextmanager

from geoalchemy2 import Geography
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

# Base for all table.
Base = declarative_base()

# Database credentials.
DATABASE_URL = os.environ.get('DATABASE_URL')

# Basic model level logging config.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_engine():
    """Creates a database engine from our database url string."""
    return sa.create_engine(
        DATABASE_URL,
        convert_unicode=True)


def db_setup():
    """Stand tables."""
    logger.info('Standing tables.')
    Base.metadata.create_all(get_engine())


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = sa.orm.scoped_session(
        sa.orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()))
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class User(Base):
    """A user represents an individual user of the application."""

    __tablename__ = 'users'

    id = sa.Column(sa.BigInteger, primary_key=True)
    given_name = sa.Column(sa.String(75))
    surname = sa.Column(sa.String(75))
    avatar = sa.Column(sa.String(200))

    # Only supporting one service for now
    # Seperating columns so we can look up by (service, uid)
    login_service = sa.Column(sa.types.String(50))
    login_uid = sa.Column(sa.types.String(75))
    login_secret = sa.Column(sa.types.JSON) # Seperate security level for secrets
    login_info = sa.Column(sa.types.JSON)

    def __str__(self):
        return '<[{}] User {} {}>'.format(
            self.id, self.given_name, self.surname
        )


class Event(Base):
    """An event represents an event managed by the API."""

    __tablename__ = 'events'

    id = sa.Column(
        sa.BigInteger,
        primary_key=True
    )

    start_time = sa.Column(sa.types.DateTime())
    end_time = sa.Column(sa.types.DateTime())
    start_time_local = sa.Column(sa.types.DateTime())
    end_time_local = sa.Column(sa.types.DateTime())
    timezone = sa.Column(sa.String(50))
    location = sa.Column(Geography(geometry_type='POINT', srid=4326))
    title = sa.Column(sa.String(200))
    attendees = sa.Column(sa.types.JSON)
    capacity = sa.Column(sa.Integer())
    logo = sa.Column(sa.types.JSON)
    url = sa.Column(sa.String(200))
    description_text = sa.Column(sa.Text())
    description_html = sa.Column(sa.Text())
    is_free = sa.Column(sa.Boolean())
    online_event = sa.Column(sa.Boolean())
    category_id = sa.Column(
        sa.BigInteger(),
        sa.ForeignKey("categories.category_id"),
        nullable=True  # eventbrite has null categories :(
    )

    def __str__(self):
        return '<[{}] Event {}>'.format(
            self.id, self.title
        )


class Category(Base):
    """An category represents an event genre as specifed by eventbrite."""

    __tablename__ = 'categories'

    category_id = sa.Column(
        sa.BigInteger,
        primary_key=True
    )

    name = sa.Column(sa.String(50), nullable=False)

    def __str__(self):
        return '<[{}] Category {}>'.format(
            self.id, self.title
        )
