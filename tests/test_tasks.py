import datetime as dt
import json
import os
from unittest.mock import patch

from beluga import db_session
from beluga.models import Event
from worker import fetch_events, load_event
from tests import FIXTURES_DIR


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


@patch('worker.Eventbrite', new=MockEventbrite)
@patch('worker.load_event.delay')
def test_fetch_events(mock_load_event_delay):
    fetch_events(lat=1, lon=2, rad=3)
    assert mock_load_event_delay.call_count == 5


def test_load_event():
    event = dict(
        title='So much good stuff',
        start_time=dt.datetime(2016, 5, 5, 1, 2),
        end_time=dt.datetime(2016, 5, 5, 1, 7),
        location={
            'lat': 1,
            'lon': 2,
            'title': 'location title'
        }
    )

    load_event(event)

    result = db_session.query(Event).one()

    assert result.title == event['title']
    assert result.start_time == event['start_time']
    assert result.end_time == event['end_time']
    assert result.location == event['location']
