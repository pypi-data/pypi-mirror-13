from .exceptions import ValidationError

from datetime import (datetime, date)
import numbers
import six


def check_length(field, value):
    if field.min_length and len(value) < field.min_length:
        raise ValidationError(
            '{} is too short. Min length is {}'.format(value, field.min_length)
        )
    if field.max_length and len(value) > field.max_length:
        raise ValidationError(
            '{} is too long. Max length is {}'.format(value, field.max_length)
        )
    return value


def is_datetime(field, value):
    if not isinstance(value, datetime):
        raise ValidationError(
            '{} must be a datetime object.'.format(field.name)
        )
    return value


def is_date(field, value):
    if not isinstance(value, date) or isinstance(value, datetime):
        raise ValidationError(
            '{} must be a date object.'.format(field.name)
        )
    return value


def is_bool(field, value):
    if not isinstance(value, bool):
        raise ValidationError(
            '{} must be a bool object.'.format(field.name)
        )
    return value


def is_set(field, value):
    if not isinstance(value, set):
        raise ValidationError(
            '{} must be a set object.'.format(field.name)
        )
    return value


def is_dict(field, value):
    if not isinstance(value, dict):
        raise ValidationError(
            '{} must be a dict object.'.format(field.name)
        )
    return value


def is_list(field, value):
    if not isinstance(value, (list, tuple)):
        raise ValidationError(
            '{} must be a list or tuple object.'.format(field.name)
        )
    return value


def is_int(field, value):
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            '{} must be an int object.'.format(field.name)
        )
    return value


def is_float(field, value):
    if not isinstance(value, float):
        raise ValidationError(
            '{} must be a float object.'.format(field.name)
        )
    return value


def is_number(field, value):
    if not isinstance(value, numbers.Number) or isinstance(value, bool):
        raise ValidationError(
            '{}, must be a number.'.format(field.name)
        )
    return value


def is_char(field, value):
    if not isinstance(value, six.string_types):
        raise ValidationError(
            '{} must be a char object.'.format(field.name)
        )
    return value
