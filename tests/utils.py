import sqlalchemy.dialects.postgresql as psql

from beluga.models import Base, session_scope, Category


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
        """Executes the wrapped version of the function.
        Clears all tables, runs function (typically a test),
        then clears tables again.
        """
        def wrapped_f(*args):
            self.add_categories()
            f(*args)
        return wrapped_f
