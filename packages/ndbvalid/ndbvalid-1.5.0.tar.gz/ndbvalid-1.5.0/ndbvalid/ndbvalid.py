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


def ip_address(ipv4=True, ipv6=False):
    """
    IP Adress validator.

    :param ipv4: If True, accept IPv4 addresses as valid (default True)
    :param ipv6: If True, accept IPv6 addresses as valid (default False)
    """
    def ip_address_validator(prop, value):
        if not (ipv4 or ipv6):
            raise ValueError('IP Address validator must have at least one of ipv4 or ipv6 enabled')

        if ipv4 and _check_ipv4(value):
            return None
        if ipv6 and _check_ipv6(value):
            return None

        raise NdbValidationError('Invalid IP address')

    return ip_address_validator


def email():
    """
    Email validator.
    Uses very primitive regular expression
    and should only be used in instances where you later verify by
    other means.
    """
    def email_validator(prop, value):
        regex = r'^.+@([^.@][^@]+)$'
        match = re.match(regex, value)

        if not match:
            raise NdbValidationError('Inavalid email address')

        if not _validate_hostname(match.group(1)):
            raise NdbValidationError('Inavalid email address')
        return None
    return email_validator


def url(require_tld=True):
    """
    Simple regexp based url validation.
    You probably want to validate the url later by other means if the url
    must resolve.

    :param require_tld: If True, then the domain nam portion of the URL must contain
                        a .tld suffix. Set this to false if you want to allow domains
                        like `localhost`.
    """
    def url_validator(prop, value):
        regex = r'^[a-z]+://(?P<host>[^/:]+)(?P<port>:[0-9]+)?(?P<path>\/.*)?$'
        match = re.match(regex, value)

        if not match:
            raise NdbValidationError('Invalid URL')

        if not _validate_hostname(match.group('host'), require_tld=require_tld, allow_ip=True):
            raise NdbValidationError('Invalid URL')
        return None
    return url_validator


def _validate_hostname(hostname, require_tld=True, allow_ip=False):
    if allow_ip:
        if _check_ipv4(hostname) or _check_ipv6(hostname):
            return True

    try:
        hostname = hostname.encode('idna')
    except UnicodeError:
        return False

    hostname = hostname.decode('ascii')

    parts = hostname.split('.')

    hostname_part = re.compile(r'^(xn-|[a-z0-9]+)(-[a-z0-9]+)*$', re.IGNORECASE)

    for part in parts:
        if not part or len(part) > 63:
            return False
        if not hostname_part.match(part):
            return False

    tld_part = re.compile(r'^([a-z]{2,20}|xn--([a-z0-9]+-)*[a-z0-9]+)$', re.IGNORECASE)

    if require_tld:
        if len(parts) < 2 or not tld_part.match(parts[-1]):
            return False

    return True


def _check_ipv4(address):
    parts = address.split('.')

    if len(parts) == 4 and all(p.isdigit() for p in parts):
        numbers = list(int(p) for p in parts)
        return all(num >=0 and num < 256 for num in numbers)
    return False

def _check_ipv6(address):
    parts = address.split(':')

    if len(parts) > 8:
        return False

    num_blank = 0
    for part in parts:
        if not part:
            num_blank += 1
        else:
            try:
                value = int(part, 16)
            except ValueError:
                return False
            else:
                if value < 0 or value > 65536:
                    return False

    if num_blank < 2:
        return True
    elif num_blank == 2 and not (parts[0] or parts[1]):
        return True
    return False
