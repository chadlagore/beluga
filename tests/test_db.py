import datetime as dt

from geoalchemy2 import WKTElement

from beluga.models import Event, session_scope
from tests.utils import new_db, add_db_categories


@new_db()
@add_db_categories([{'category_id': 1, 'name': 'new_cat'}])
def test_write_event():
    event = Event(
        title='So much good stuff',
        start_time=dt.datetime(2016, 5, 5, 1, 2),
        end_time=dt.datetime(2016, 5, 5, 1, 7),
        location=WKTElement('POINT(1 2)', srid=4326),
        category_id="1"
    )

    with session_scope() as db_session:
        db_session.add(event)
        db_session.flush()

        result = db_session.query(Event).one()

        assert result == event
