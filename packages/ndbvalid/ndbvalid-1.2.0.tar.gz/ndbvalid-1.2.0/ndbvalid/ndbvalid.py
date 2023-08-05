# -*- coding: utf-8 -*-


import re


class NdbValidationError(Exception):
    pass


def length(min=None, max=None):
    """
    Length validator.
    The string must have a minimal length of min and maximal length of max characters.

    :param min: Minimum length
    :param max: Maximal length
    :type min: int
    :type max: int
    """
    def length_validator(prop, value):
        if min and len(value) < min:
            raise NdbValidationError('{} must be greater than {} characters'.format(prop, min))
        if max and len(value) > max:
            raise NdbValidationError('{} must be less than {} characters'.format(prop, max))
        return None
    return length_validator


def number_range(min=None, max=None):
    """
    Number range validator.
    The value must be in the given range inclusive.
    This will work with any comparable number type.

    :param min: The minimum require value. If not provided, will not be checked.
    :param min: The maximum require value. If not provided, will not be checked.
    """
    def number_range_validator(prop, value):
        if min and value < min:
            raise NdbValidationError('{} must be greater than {}'.format(prop, min))
        if value > max:
            raise NdbValidationError('{} must be less than {}'.format(prop, max))
        return None
    return number_range_validator


def regexp(regex, flags=0, msg='Invaild input'):
    """
    Regular expression validator.
    String must match given regex.

    :param regex: The regular expression string to use.
    :param flags: The regex flags to use, e.g. re.IGNORECASE.
    :param msg: Error message.
    :type regex: str
    :type flags: int
    :type msg: str
    """
    def regex_validator(prop, value):
        if not re.match(regex, value, flags=flags):
            raise NdbValidationError(msg)
        return None
    return regex_validator


def mac_address():
    """
    MAC address validatior.
    """
    return regexp(r'^(?:[0-9a-fA-f]{2}:){5}[0-9a-fA-F]{2}$', msg='Invalid Mac address')


def uuid():
    """
    UUID validatior.
    """
    return regexp(r'^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$', msg='Invalid UUID')
