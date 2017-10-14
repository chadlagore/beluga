import datetime as dt
import json
import os
from unittest.mock import patch

from beluga import session_scope
from beluga.models import Event
from worker import fetch_events, load_event
from tests import FIXTURES_DIR
from tests.utils import new_db


class MockEventbrite:

    def __init__(self, token):
        pass

    def event_search(self, **data):
        with open(os.path.join(
            FIXTURES_DIR, 'events.json')
        ) as infile:
            return {
                "events": json.load(infile)
            }


def new_event_dict():
    return dict(
        id=1,
        title='So much good stuff',
        start_time=dt.datetime(2016, 5, 5, 1, 2),
        end_time=dt.datetime(2016, 5, 5, 1, 7),
        location={
            'lat': 1,
            'lon': 2,
            'title': 'location title'
        }
    )


@patch('worker.Eventbrite', new=MockEventbrite)
@patch('worker.load_event.delay')
def test_fetch_events(mock_load_event_delay):
    fetch_events(lat=1, lon=2, rad=3)
    assert mock_load_event_delay.call_count == 5


@new_db()
def test_load_event():
    """Enforce that load_event drops a new event into the 
    database.
    """
    event = new_event_dict()
    load_event(event)

    with session_scope() as db_session:
        result = db_session.query(Event).one()
        assert result.title == event['title']
        assert result.start_time == event['start_time']
        assert result.end_time == event['end_time']
        assert result.location == event['location']


@new_db()
def test_events_dont_get_clobbered():
    """Enforce that multiple event adds don't clobber existing
    events (they may have accumulated attendees in our db).
    """
    # Mock up event with attendees, insert to db.
    event_with_attendees = new_event_dict()
    event_with_attendees['attendees'] = ['alice', 'bob']
    with session_scope() as db_session:
        db_session.add(Event(**event_with_attendees))
        db_session.commit()

    # Try to inject a vanilla event without attendees.
    the_same_event = new_event_dict()
    load_event(the_same_event)
    
    # Now check whats in the db.
    with session_scope() as db_session:
        this_id = the_same_event['id']
        result = db_session.query(Event).filter(Event.id == this_id).all()
        assert len(result) == 1
        assert result[0].attendees == event_with_attendees['attendees']

