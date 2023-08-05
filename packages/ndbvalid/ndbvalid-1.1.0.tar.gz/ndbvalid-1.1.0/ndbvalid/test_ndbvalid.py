# -*- coding: utf-8 -*-


from unittest import TestCase
from . import ndbvalid
import re


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
