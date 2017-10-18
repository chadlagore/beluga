import datetime as dt
import json
import logging

from celery import Celery
from eventbrite import Eventbrite
import sqlalchemy.dialects.postgresql as psql

from beluga.models import Event, session_scope
from worker import config


# Create a celery worker.
celery = Celery(__name__)
celery.config_from_object(config)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setting up periodic tasks...")

    # https://www.eventbrite.com/developer/v3/api_overview/rate-limits/
    # We get 2000 calls per hour.
    sender.add_periodic_task(
        config.COLLECTION_INTERVAL,
        fetch_events.s(
            lat=config.VANCOUVER_LAT,
            lon=config.VANCOUVER_LON,
            rad=config.VANCOUVER_RAD
        ),
        expires=60
    )


@celery.task(bind=True)
def fetch_events(self, lat, lon, rad, **params):
    """Fetches events for a circle around the given coordinate
    of radius `rad'.

    Args:
        lat (str): A latitude for the centroid coordinate.
        lon (str): A longitude for the centroid coordinate.
        rad (str): A radius for the circle.
        **params : Additional paramters to be passed to the
            eventbrite client.

    TODO: Deal with pagination from eventbrite.
    """
    assert config.EVENTBRITE_APP_KEY, \
        'Must set EVENTBRITE_APP_KEY to run eventbrite tasks'

    eb = Eventbrite(config.EVENTBRITE_APP_KEY)

    logger.info("Starting event collection.")

    # Build request.
    data = {
        "location.latitude": str(lat),
        "location.longitude": str(lon),
        "location.within": str(rad),
    }

    # Add additional parameters.
    data.update(params)

    # Request.
    result = eb.event_search(**data)

    # Produce a new task to load every event.
    with session_scope() as db_session:
        for event in result['events']:
            start = dt.datetime.strptime(
                event['start']['utc'],
                config.EVENTBRITE_DATE_FMT)

            end = dt.datetime.strptime(
                event['end']['utc'],
                config.EVENTBRITE_DATE_FMT)

            new_event = dict(
                id=event['id'],
                title=event['name']['text'],
                start_time=start,
                end_time=end,
                location=json.dumps({
                    "lat": lat,
                    "lon": lon,
                    "venue_id": event['venue_id']
                })
            )

            # Load event into database.
            load_event(new_event, db_session)

    return result


def load_event(event_params, session):
    """Loads an event into the Events table.
    Will update events on confict.

    Args:
        event_params (dict): A set of event parameters.
        session (sa.scoped_session): A SQLAlchemy session.
    """
    # Basic insert statement.
    insert_stmt = psql.insert(Event).values(**event_params)

    # Our ON CONFLICT DO UPDATE clause.
    on_conflict_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[Event.id],
        set_=event_params)

    # Add to database.
    session.execute(on_conflict_stmt)


@celery.task()
def clear_old_events():
    """Clear events whose end_time has passed."""
    with session_scope() as db_session:
        stmt = (Event.__table__
                     .delete()
                     .where(Event.end_time < dt.date.today()))
        db_session.execute(stmt)
