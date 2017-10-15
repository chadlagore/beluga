import datetime as dt

from beluga.models import Event
from beluga import session_scope
from tests.utils import new_db


@new_db()
def test_write_event():
    event = Event(
        title='So much good stuff',
        start_time=dt.datetime(2016, 5, 5, 1, 2),
        end_time=dt.datetime(2016, 5, 5, 1, 7),
        location={
            'lat': 1, 
            'lon': 2, 
            'title': 'location title'
        }
    )

    with session_scope() as db_session:
        db_session.add(event)
        db_session.flush()

        result = db_session.query(Event).one()

        assert result == event
