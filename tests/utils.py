from beluga import session_scope, Base


class new_db:
    """A decorator for clearing the database before and
    after a function call (presumably a test).
    """

    def __init__(self):
        pass

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
