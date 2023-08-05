from django.db import IntegrityError
from rest_framework.exceptions import APIException, ValidationError


class ServerError(APIException):
    status_code = 500
    default_detail = 'Service malfunction, please try again later.'


class TransitionError(ValidationError, IntegrityError):
    pass
