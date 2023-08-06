import unittest
from mock import Person
from models import PostgreSQLTypes


class TestModelMethods(unittest.TestCase):

    def test_to_json(self):
        fake = Person(name='testa', age=10)
        self.assertEqual({'active': None, 'age': 10, 'gender': None, 'lastname': None, 'name': 'testa', 'uuid': None, 'weight': 23}, fake.to_json())

    def test_to_instance(self):
        model_json = {'name': 'john', 'age': 53}
        instance = Person.to_instance(model_json)
        self.assertTrue(isinstance(instance, Person))
        self.assertEqual(instance.name, 'john')
        self.assertEqual(instance.age, 53)

    def test_create_table(self):
        types = [PostgreSQLTypes.char, PostgreSQLTypes.boolean,
                 PostgreSQLTypes.real, PostgreSQLTypes.int]
        sql = "CREATE TABLE tb_Person (uuid {0}(36) PRIMARY KEY, \
active {1}, age {3}, gender {0}, lastname {0}(140), name {0}(512), weight {2});".format(*types)
        self.assertEqual(sql, Person.create_table_sql())

    def test_columns(self):
        self.assertEqual(['active', 'age', 'gender', 'lastname', 'name', 'uuid', 'weight'], Person.columns())
        p = Person()
        self.assertEqual(['active', 'age', 'gender', 'lastname', 'name', 'uuid', 'weight'], p.columns())
