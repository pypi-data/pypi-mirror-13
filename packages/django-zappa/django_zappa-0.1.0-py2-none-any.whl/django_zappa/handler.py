from __future__ import unicode_literals

import json
import mimetypes
import os
import re
import sys
import zipfile

from copy import copy
from importlib import import_module
from io import BytesIO


from django.apps import apps
from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import ISO_8859_1, UTF_8, WSGIRequest
from django.core.signals import (
    got_request_exception, request_finished, request_started,
)
from django.db import close_old_connections

from zappa.wsgi import create_wsgi_request

class LambdaHandler(BaseHandler):
    """
    A HTTP Handler that can be used for testing purposes. Uses the WSGI
    interface to compose requests, but returns the raw HttpResponse object with
    the originating WSGIRequest attached to its ``wsgi_request`` attribute.
    """
    def __init__(self, enforce_csrf_checks=True, *args, **kwargs):
        self.enforce_csrf_checks = enforce_csrf_checks
        super(LambdaHandler, self).__init__(*args, **kwargs)

    def __call__(self, environ):
        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._request_middleware is None:
            self.load_middleware()

        request_started.disconnect(close_old_connections)
        request_started.send(sender=self.__class__, environ=environ)
        request_started.connect(close_old_connections)
        request = WSGIRequest(environ)
        # sneaky little hack so that we can easily get round
        # CsrfViewMiddleware.  This makes life easier, and is probably
        # required for backwards compatibility with external tests against
        # admin views.
        request._dont_enforce_csrf_checks = not self.enforce_csrf_checks

        # Request goes through middleware.
        response = self.get_response(request)
        # Attach the originating request to the response so that it could be
        # later retrieved.
        response.wsgi_request = request

        # We're emulating a WSGI server; we must call the close method
        # on completion.
        if response.streaming:
            response.streaming_content = closing_iterator_wrapper(
                response.streaming_content, response.close)
        else:
            request_finished.disconnect(close_old_connections)
            response.close()                    # will fire request_finished
            request_finished.connect(close_old_connections)

        return response

def lambda_handler(event, context):    
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zappa_settings")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helloworld.settings")
    import django
    django.setup()

    handler = LambdaHandler()
    environ = create_wsgi_request(event)
    response = handler(environ)
    print response
    print dir(response)

    returnme = {'Body': response.content}
    return returnme

if __name__ == "__main__":
    lambda_handler(event, None)
