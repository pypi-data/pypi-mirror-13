import unittest
from mock import Person, Gender
from models import BaseProperty


class TestProperty(unittest.TestCase):

    def test_enum_property(self):
        model = Person()
        model.gender = Gender.male
        self.assertEquals(model.gender, Gender.male)

        with self.assertRaises(ValueError):
            a = Person()
            a.gender = "invalid valid"

    def test_property(self):
        with self.assertRaises(ValueError):
            obj = Person()
            obj.name = 3

        with self.assertRaises(ValueError):
            obj = Person()
            obj.age = "a"

        obj = Person()
        obj.name = "string"
        obj.age = 1

        self.assertEqual(obj.name, "string")
        self.assertEqual(obj.age, 1)

    def test_different_object(self):
        obj1 = Person()
        obj1.name = "string"
        obj1.age = 1

        self.assertEqual(obj1.name, "string")
        self.assertEqual(obj1.age, 1)

        obj2 = Person()
        obj2.name = "new"
        obj2.age = 2

        self.assertEqual(obj2.name, "new")
        self.assertEqual(obj2.age, 2)

        self.assertEqual(obj1.name, "string")
        self.assertEqual(obj1.age, 1)

    def test_wrong_implementation_of_property(self):
        class WrongProp(BaseProperty):
            pass

        with self.assertRaises(NotImplementedError):
            WrongProp()._type()
