from django.db import connection, connections
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def replace_default_backend():

    if not hasattr(settings, 'DATABASES'):
        return

    db_conf = settings.DATABASES
    if 'default' in db_conf:
        def_db_conf = db_conf['default']
        db_engine = def_db_conf['ENGINE']

        if 'mysql' in db_engine:
            def_db_conf['ENGINE'] = 'sql_debugger.backends.mysql'
        else:
            raise ImproperlyConfigured()

        settings.SOUTH_DATABASE_ADAPTERS = {
            'default': 'south.db.mysql',
        }

if settings.DEBUG and settings.SQL_DEBUGGER_SHOW_TRACEBACK:
    if hasattr(connections, 'default'):
        del connections['default'] # rude but effective
    replace_default_backend()
