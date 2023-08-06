import unittest
from enum import Enum


class FakeEnum(Enum):
    an_prop = 'value'
    _private_prop = 'private_value'


class TestEnum(unittest.TestCase):

    def test_to_value(self):
        self.assertEqual(FakeEnum.to_value('an_prop'), 'value')
        with self.assertRaises(Exception):
            FakeEnum.to_value('wrong_prop')

    def test_keys_value(self):
        result = {'an_prop': 'value'}
        self.assertEqual(FakeEnum.keys_values(), result)

    def test_values(self):
        values = ['value']
        self.assertEqual(FakeEnum.values(), values)

    def test_exists(self):
        self.assertTrue(FakeEnum.exist('an_prop'))
        self.assertFalse(FakeEnum.exist('_private_prop'))
