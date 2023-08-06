import functools
from django.conf import settings

replace_pairs = getattr(settings, 'REWRITEBODY_PAIRS', [])


def do_replace(content, before_after):
    before, after = before_after
    return content.replace(before, after)


class RwriteBodyMiddleware(object):
    def process_response(self, request, response):
        if response.has_header('Content-Type') and 'text/html' in response['Content-Type']:
            response.content = functools.reduce(do_replace, replace_pairs, response.content)
        return response
