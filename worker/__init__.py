import datetime as dt
import json
import logging

from celery import Celery
from eventbrite import Eventbrite

from beluga import get_db_session
from beluga.models import Event
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
            title=event['name']['text'],
            start_time=start,
            end_time=end,
            location=json.dumps({
                "lat": lat,
                "lon": lon,
                "venue_id": event['venue_id']
            })
        )

        load_event.delay(new_event)

    return result


@celery.task(bind=True)
def load_event(self, event_params):
    """Loads an event into the Events table.

    Args:
        event (Event): An event.
    """
    _, db_session = get_db_session()
    db_session.add(Event(**event_params))
    db_session.flush()
