import json

from django import template
from django.db import connections, connection
from django.conf import settings


register = template.Library()

class SQLDebugInfo(template.Node):

    def render(self, context):
        return json.dumps(connection.queries)

def sql_debug_info(parser, token):
    return SQLDebugInfo()

register.tag('sql_debug_info', sql_debug_info)