import json

import sqlalchemy.dialects.postgresql as psql

from beluga import config as conf
from beluga.models import (
    Base, session_scope, Category, Event, User
)
from worker import prepare_event


class new_db:
    """A decorator for clearing the database before and
    after a function call (presumably a test).
    """

    def clear_tables(self):
        meta = Base.metadata
        with session_scope() as session:
            for table in reversed(meta.sorted_tables):
                session.execute(table.delete())
            session.commit()

    def __call__(self, f):
        """Executes the wrapped version of the function.
        Clears all tables, runs function (typically a test),
        then clears tables again.
        """
        def wrapped_f(*args):
            self.clear_tables()
            f(*args)
            self.clear_tables()
        return wrapped_f


class add_db_categories:
    """A decorator for adding categories to a database."""

    def __init__(self, cats):
        self.cats = cats

    def add_categories(self):
        with session_scope() as session:
            for i in self.cats:
                stmt = (
                    psql.insert(Category)
                        .values(**i)
                        .on_conflict_do_update(
                            index_elements=[Category.category_id],
                            set_=i))
                session.execute(stmt)

    def __call__(self, f):
        def wrapped_f(*args):
            self.add_categories()
            f(*args)
        return wrapped_f


class mock_events:
    """A decorator for adding events to a database."""

    def __init__(self):
        pass

    # Have to add the categoies before loading events
    # due to foreign key constraint.
    @add_db_categories([
        {'category_id': 102, 'name': 'new_cat1'},
        {'category_id': 101, 'name': 'new_cat2'},
        {'category_id': 114, 'name': 'new_cat3'},
        {'category_id': 117, 'name': 'new_cat4'}
    ])
    def add_events(self):
        """Collect fake events and venues, load into DB."""
        with session_scope() as session:
            with open('tests/fixtures/events.json') as infile:
                events = json.load(infile)

            # Fake the venue for now.
            venue = {
                "latitude": conf.DEFAULT_LAT,
                "longitude": conf.DEFAULT_LON
            }

            # Add events, if they're already there from calling this
            # decorator earlier, do update.
            for e in events:
                prepped = prepare_event(e, venue)
                q = (psql.insert(Event).values(**prepped)
                         .on_conflict_do_update(
                             index_elements=[Event.id],
                             set_=prepped))
                session.execute(q)

    def __call__(self, f):
        def wrapped_f(*args):
            self.add_events()
            f(*args)
        return wrapped_f

class mock_users:
    """A decorator for adding users to a database."""

    def __init__(self):
        pass

    # Have to add the categoies before loading events
    # due to foreign key constraint.
    @add_db_categories([
        {'category_id': 102, 'name': 'new_cat1'},
        {'category_id': 101, 'name': 'new_cat2'},
        {'category_id': 114, 'name': 'new_cat3'},
        {'category_id': 117, 'name': 'new_cat4'}
    ])
    def add_events(self):
        """Collect fake users, load into DB."""
        with session_scope() as session:
            with open('tests/fixtures/users.json') as infile:
                users = json.load(infile)

            for u in users:
                q = psql.insert(User).values(
                    id=u['id'],
                    given_name=u['given_name'],
                    surname=u['surname']
                )
                session.execute(q)

    def __call__(self, f):
        def wrapped_f(*args):
            self.add_events()
            f(*args)
        return wrapped_f
