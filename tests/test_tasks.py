import json
import os
from unittest.mock import patch

from worker import fetch_events
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
@patch('worker.load_event')
def test_fetch_events(mock_load_event):
    result = fetch_events(lat=1, lon=2, rad=3)
    assert result
