import json
from django.db import connections, connection
from django.conf import settings

class SQLDebugMiddleware(object):

    def process_response(self, request, response):

        if not settings.DEBUG:
            return response

        if request.is_ajax(): #TODO: if not JSON?

            if response.status_code / 100 == 2:
                try:
                    resp_d = json.loads(response.content)
                    resp_d['path'] = request.get_full_path()
                    resp_d['sql_debug_info'] = connection.queries
                    response.content = json.dumps(resp_d)
                except Exception, e:
                    pass
            else:
                parts = {
                    "traceback": "Traceback"
                }

                empty_line = '\n\n'
                resp_parts = response.content.split(empty_line)
                res = { "error": resp_parts[0] }

                for rp in resp_parts:
                    for k,p in parts.iteritems():
                        if rp.startswith(p):
                            res[k] = rp

                response.content = json.dumps({"errordata": res, "path": request.get_full_path()})

        return response
