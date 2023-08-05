# -*- coding: utf-8 -*-


from unittest import TestCase
from . import ndbvalid
import re
import uuid


class TestValidators(TestCase):

    def test_length_validator(self):
        validator = ndbvalid.length(min=7, max=15)

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'short')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'too loooooong string')

        self.assertIsNone(validator({}, 'normal string'))

    def test_number_range_validator(self):
        validator = ndbvalid.number_range(min=7, max=68.69)

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 1)
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 100)
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 1.2)
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 100.30)

        self.assertIsNone(validator({}, 42))
        self.assertIsNone(validator({}, 42.42))
        self.assertIsNone(validator({}, 7))
        self.assertIsNone(validator({}, 68.69))

    def test_regex_validator(self):
        validator = ndbvalid.regexp(r'[a-z]+')

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '1')

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'Invalid')

        self.assertIsNone(validator({}, 'valid'))

        validator = ndbvalid.regexp(r'[a-z]+', re.IGNORECASE)

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '1')

        self.assertIsNone(validator({}, 'Valid'))

    def test_mac_address_validator(self):
        validator = ndbvalid.mac_address()

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '00:FC:34:ad:78')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '00:FC:34:ad78:0D')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '00:FC:34:ad:78:0D:')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '00:GC:34:ad:78:0D:')

        self.assertIsNone(validator({}, '00:FC:34:ad:78:0D'))

    def test_uuid_validator(self):
        validator = ndbvalid.uuid()
        test_uuid = str(uuid.uuid4())

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, test_uuid[0:5])
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, test_uuid * 2)
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '')

        self.assertIsNone(validator({}, str(uuid.uuid4())))

    def test_ip_address_validator(self):
        validator = ndbvalid.ip_address()

        with self.assertRaises(ValueError):
            invalid_validator = ndbvalid.ip_address(False, False)
            invalid_validator({}, '127.0.0.1')

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '127.0.0.')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '127.0.0.1.1')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '127.a.0.1')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '127001')

        self.assertIsNone(validator({}, '127.0.0.1'))
        self.assertIsNone(validator({}, '192.168.0.1'))
        self.assertIsNone(validator({}, '8.8.8.8'))

        validator = ndbvalid.ip_address(ipv6=True)

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'ff:ff:ff:ff:ff:ff:ff:ff:ff')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'ff::::ff:ff:ff:ff')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'ff:::-42:ff:ff:ff:ff')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'ff:ff:ff:zz:ff:ff:ff:ff')

        self.assertIsNone(validator({}, 'ff:ff:ff:ff:ff:ff:ff:ff'))
        self.assertIsNone(validator({}, 'ff:ff:ff::ff:ff:ff:ff'))
        self.assertIsNone(validator({}, '::ff:ff:ff:ff:ff:ff'))

    def test_url(self):
        validator = ndbvalid.url()

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'http://192.168.0')
        with self.assertRaises(ndbvalid.NdbValidationError):
            host = 'a' * 64
            validator({}, 'http://{}'.format(host))
        with self.assertRaises(ndbvalid.NdbValidationError):
            host = 'a.' * 64
            validator({}, 'http://{}'.format(host))
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'http://localhost')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'localhost')

        self.assertIsNone(validator({}, 'http://192.168.0.1'))
        self.assertIsNone(validator({}, 'http://google.com'))
        self.assertIsNone(validator({}, 'http://wikipedia.org'))
        self.assertIsNone(validator({}, 'http://google.com:80/test/path?id=1'))

        validator = ndbvalid.url(require_tld=False)
        self.assertIsNone(validator({}, 'http://localhost'))
        self.assertIsNone(validator({}, 'http://google.com'))
        self.assertIsNone(validator({}, 'http://wikipedia.org'))

    def test_validate_hostname(self):
        self.assertTrue(ndbvalid._validate_hostname('192.168.0.1', allow_ip=True))
        self.assertTrue(ndbvalid._validate_hostname('ff:ff:ff:ff:ff:ff:ff:ff', allow_ip=True))

        self.assertFalse(ndbvalid._validate_hostname('192.168.0.1', allow_ip=False))
        self.assertFalse(ndbvalid._validate_hostname('ff:ff:ff:ff:ff:ff:ff:ff', allow_ip=False))

    def test_email_validator(self):
        validator = ndbvalid.email()

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'localhost')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'google.com')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'user@localhost')

        self.assertIsNone(validator({}, 'user@test.com'))
        self.assertIsNone(validator({}, 'olexander.yermakov@gmail.com'))
        self.assertIsNone(validator({}, 'test42@gmail.com'))

    def test_all(self):
        validator = ndbvalid._and(ndbvalid.length(min=5), ndbvalid.regexp(r'^[0-9]+$'))

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '123')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, '123abc')

        self.assertIsNone(validator({}, '12345'))

    def test_or(self):
        validator = ndbvalid._or(ndbvalid.length(min=5, max=6), ndbvalid.ip_address(), ndbvalid.regexp(r'^[0-9]+$'))

        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'abc')
        with self.assertRaises(ndbvalid.NdbValidationError):
            validator({}, 'abcdefgh')

        self.assertIsNone(validator({}, '12345'))
        self.assertIsNone(validator({}, '12'))
        self.assertIsNone(validator({}, '123abc'))
        self.assertIsNone(validator({}, '127.0.0.1'))
