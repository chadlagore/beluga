import datetime as dt
import logging

from celery import Celery
from eventbrite import Eventbrite
from geoalchemy2 import WKTElement
import sqlalchemy

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
    # We get 2000 calls per hour - this is doing 180.
    sender.add_periodic_task(
        20,
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
            lat=lat,
            lon=lon
        )

        load_event.delay(new_event)

    return result


@celery.task(bind=True)
def load_event(self, event_params):
    """Loads an event into the Events table.
    Will not clobber existing events.

    Args:
        event (Event): An event.
    """
    try:
        with session_scope() as db_session:
            event_params['location'] = WKTElement(
                'POINT({} {})'.format(
                    event_params.pop('lat'),
                    event_params.pop('lon')),
                srid=4326
            )
            db_session.add(Event(**event_params))
    except sqlalchemy.exc.IntegrityError:
        pass
