import unittest
from models import ModelBasicProtocol


class TestModelIsImplementingMeta(unittest.TestCase):

    def __get_wrong_class(self):
        class Fake(object):
            __metaclass__ = ModelBasicProtocol

            def __init__(self, a):
                pass

        return Fake

    def __get_right_class(self):
        class Fake(object):
            __metaclass__ = ModelBasicProtocol

            def __init__(self, name=None):
                pass

        return Fake

    def __get_other_right_class(self):
        class Fake(object):
            __metaclass__ = ModelBasicProtocol

            def __init__(self):
                pass

        return Fake

    def test_is_implementing(self):

        with self.assertRaises(Exception):
            self.__get_wrong_class()(1)

        self.assertIsNotNone(self.__get_right_class()())
        self.assertIsNotNone(self.__get_other_right_class()())

        self.assertEqual('Fake', self.__get_other_right_class().__name__)
