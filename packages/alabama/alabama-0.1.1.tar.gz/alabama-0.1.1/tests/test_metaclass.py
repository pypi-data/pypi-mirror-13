import unittest
from models import ModelBasicProtocol, BaseModel, StringProperty


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


class TestBehaviorOfModelBasicProtocol(unittest.TestCase):

    def test_properties_details_method(self):
        class Animal(BaseModel):
            specie = StringProperty()

        class Dog(Animal):
            name = StringProperty()

        rex = Dog()
        properties = rex._properties_details

        self.assertTrue('specie' in properties)
        self.assertTrue('name' in properties)
