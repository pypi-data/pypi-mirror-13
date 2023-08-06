import functools
from django.conf import settings

replace_pairs = getattr(settings, 'REWRITEBODY_PAIRS', [])

class RwriteBodyMiddleware(object):
    def process_response(self, request, response):
        response.content = functools.reduce(
            lambda content, (before, after): content.replace(before, after),
            response.content,
            )
