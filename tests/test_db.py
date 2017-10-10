import datetime as dt

from beluga.models import Event
from beluga import db_session


def test_write_event():
    event = Event(
        title='So much good stuff',
        start_time=dt.datetime(2016, 5, 5, 1, 2),
        end_time=dt.datetime(2016, 5, 5, 1, 7)
    )

    db_session.add(event)
    db_session.flush()

    result = db_session.query(Event).one()

    assert result == event
