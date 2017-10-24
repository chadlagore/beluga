import datetime as dt
import logging

from celery import Celery
from celery.schedules import crontab
from eventbrite import Eventbrite
from geoalchemy2 import WKTElement
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

    # Schedule cleanup  at the beginning of each day.
    sender.add_periodic_task(
        crontab(hour=0, minute=5),
        clear_old_events.s()
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

    # Find out how many pages to collect.
    pagination = eb.event_search(**data)['pagination']
    num_pages = pagination['page_count']
    to_collect = min(num_pages, config.EVENTBRITE_EVENT_PAGES)

    # Produce a new task to load every event.
    with session_scope() as db_session:

        # Collect several pages.
        logger.info('Collecting {} pages'.format(num_pages))
        logger.info(pagination)
        for page in range(1, to_collect+1):

            # Collect this page.
            data.update({'page': page})
            result = eb.event_search(**data)
            logger.info('{} of {} pages: collected {} events'.format(
                page, config.EVENTBRITE_EVENT_PAGES,
                result['pagination']['page_size']
                )
            )

            for event in result['events']:

                # Collect venue for lat/lon.
                venue = eb.get('/venues/{}'.format(event['venue_id']))

                # Build a payload with each event.
                new_event = dict(
                    id=event['id'],
                    title=event['name']['text'],
                    start_time=event['start']['utc'],
                    end_time=event['end']['utc'],
                    start_time_local=event['start']['local'],
                    end_time_local=event['end']['local'],
                    timezone=event['start']['timezone'],
                    capacity=event['capacity'],
                    location=WKTElement('POINT({} {})'.format(
                        venue['longitude'],
                        venue['latitude']
                    )),
                    logo=event['logo'],
                    url=event['url'],
                    description_text=event['description']['text'],
                    description_html=event['description']['html'],
                    is_free=event['is_free'],
                    online_event=is_online(event, venue)
                )

                # Load event into database.
                load_event(new_event, db_session)

    return result


def is_online(event, venue):
    """Returns true if the event is online.
    Eventbrite is a bit inconsistent with this
    in the event object itself, so as a backup,
    check if lat/lon are zero.
    """
    lat = float(venue['latitude'])
    lon = float(venue['longitude'])
    return event['online_event'] or (lat == 0 and lon == 0)


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
    cutoff = dt.date.today() - dt.timedelta(days=config.STALE_EVENT_DAYS)
    with session_scope() as db_session:
        stmt = (Event.__table__
                     .delete()
                     .where(Event.end_time < cutoff))
        db_session.execute(stmt)
