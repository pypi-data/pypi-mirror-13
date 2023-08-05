import traceback, datetime, time

from django.db.backends.mysql.base import DatabaseWrapper, CursorWrapper
from django.db.backends import util
from django.conf import settings

class TracebackCursorWrapper(util.CursorWrapper):

    def __init__(self, cursor, db):
        super(TracebackCursorWrapper, self).__init__(cursor, db)
    
    def execute(self, sql, params=None):

        try:
            return super(TracebackCursorWrapper, self).execute(sql, params)
        finally:

            tstack = traceback.extract_stack()
            last_app_call_pos = 0
            for i,t_tup in enumerate(tstack):
                if t_tup[0].startswith(settings.BASE_DIR):
                    last_app_call_pos = i

            ts = time.mktime(datetime.datetime.now().timetuple())

            sqlex = self.db.ops.last_executed_query(self.cursor, sql, params)
            self.db.queries.append({
                "sql": sqlex,
                "tb": tstack[0:last_app_call_pos + 1],
                "ts": ts
            })


class TracebackDatabaseWrapper(DatabaseWrapper):

    def __init__(self, *args, **kwargs):
        super(TracebackDatabaseWrapper, self).__init__(*args, **kwargs)
        self.use_debug_cursor = False

    def cursor(self):
        self.validate_thread_sharing()
        cursor = TracebackCursorWrapper(self._cursor(), self)
        return cursor

    def create_cursor(self):
        cursor = self.connection.cursor()
        return CursorWrapper(cursor)


DatabaseWrapper = TracebackDatabaseWrapper
    