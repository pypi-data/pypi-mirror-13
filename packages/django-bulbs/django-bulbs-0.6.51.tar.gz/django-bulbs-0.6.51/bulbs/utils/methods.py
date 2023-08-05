from dateutil import tz
from six import string_types, text_type, binary_type

from django.conf import settings
from django.utils import timezone


def get_central_now():
    utc_now = timezone.now()
    central_tz = tz.gettz('America/Chicago')
    central_now = utc_now.astimezone(central_tz)
    return central_now


def today():
    # catching this because settings.TODAY might literally be None in tests
    # getattr will return None if the value is set to None
    return getattr(settings, "TODAY", get_central_now())


def get_query_params(request):
    try:
        return request.query_params
    except:
        return request.QUERY_PARAMS


def get_request_data(request):
    try:
        return request.data
    except:
        return request.DATA


def is_str(value):
    return isinstance(value, (string_types, text_type, binary_type))


def is_valid_digit(value):
    if isinstance(value, (int, float)):
        return True
    elif is_str(value):
        return value.isdigit()
    return False
