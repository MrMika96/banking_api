import logging
from pprint import pformat

from django.db import connection
from django.utils.deprecation import MiddlewareMixin

from banking_api import settings

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Function what returns client ip."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class PrintSqlQuery(MiddlewareMixin):
    def process_response(self, request, response):
        """Function what will return info about a request to our API."""
        if settings.DEBUG and settings.LOCAL and len(connection.queries) > 0:
            from pygments import highlight
            from pygments.formatters.terminal import TerminalFormatter
            from pygments.lexers.sql import SqlLexer
            from pygments_pprint_sql import SqlFilter

            queries = connection.queries
            lexer = SqlLexer()
            lexer.add_filter(SqlFilter())

            totsecs = 0.0
            logger.info(f"Client IP: {get_client_ip(request)}")
            request_no_auth = {
                x: request.headers[x]
                for x in request.headers
                if x not in ["Authorization", "Cookie"]
            }
            logger.info(f"Request headers:\n{pformat(request_no_auth)}")
            for query in queries:
                logger.info(query["time"], "used on:")
                totsecs += float(query["time"])
                logger.info(
                    highlight(query["sql"], lexer, TerminalFormatter())
                )

            logger.info(
                f"Number of queries: {len(queries)}\n"
                f"Total time: {totsecs}"
            )
        return response
