# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import logging
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.views import exception_handler as default_exception_handler
from rest_framework.response import Response

log = logging.getLogger(__name__)

def exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = default_exception_handler(exc, context)

    if response is None:
        # Capture Oauthlib exceptions
        try:
            # noinspection PyUnresolvedReferences
            from oauthlib.oauth2.rfc6749.errors import OAuth2Error
            if isinstance(exc, OAuth2Error):
                response = Response({'detail': exc.error}, status=exc.status_code)
        except:
            pass

    # Now add the HTTP status code to the response.
    if response is not None:
        if isinstance(response.data, dict):
            response.data['code'] = response.status_code
            response.data['error'] = response.data.pop('detail', None)
        elif isinstance(response.data, list):
            response.data = {'error': response.data.pop(), 'code': response.status_code}

    if response:
        log.error("Framework exception ({}) occurred: {}".format(response.status_code, exc))

    return response


class APIUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Service temporarily unavailable')


class ResourceGone(APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _('No longer available')

class InvalidSession(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Your Session has expired, you will need to login again")