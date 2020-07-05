from psycopg2 import extensions as _ext

class Cursor(_ext.cursor):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return

class Connection(_ext.connection):
    def init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_factory = Cursor

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return