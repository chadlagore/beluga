import sqlalchemy as sa

from beluga import Base


class User(Base):
    """A user represents an individual user of the application."""

    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    given_name = sa.Column(sa.String(75))
    surname = sa.Column(sa.String(75))
    logins = sa.Column(sa.types.JSON)
    avatar = sa.Column(sa.String(200))

    def __str__(self):
        return '<[{}] User {} {}>'.format(
            self.id, self.given_name, self.surname
        )


class Event(Base):
    """An event represents an event managed by the API."""

    __tablename__ = 'events'

    id = sa.Column(sa.Integer, primary_key=True)
    start_time = sa.Column(sa.String(75))
    end_time = sa.Column(sa.String(75))
    location = sa.Column(sa.types.JSON)
    title = sa.Column(sa.String(200))
    attendees = sa.Column(sa.types.JSON)

    def __str__(self):
        return '<[{}] Event {} {}>'.format(
            self.id, self.given_name, self.surname
        )
