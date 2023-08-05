from mock import Age, Person, TestLoader
import storage
from storage import Query


class TestSQLInjection(TestLoader):

    def test_sql_injection(self):
        self.assertTrue(storage.insert(Age('mouse', 20)))
        test = Age("'; delete from tb_Age")
        self.assertTrue(storage.insert(test))
        test_obj = storage.find(Age, where={'name': 'mouse'})
        self.assertEqual(len(test_obj), 1)


class TestModelDefaultArgs(TestLoader):

    def test_default(self):
        self.assertTrue(storage.insert(Person('mouse', 'optico', 20, 21)))
        q = Query(Person, alias='u').select(['u.name', 'u.age'])
        p = storage.query(q)['Person'][0]
        self.assertEqual(p.weight, None)
        self.assertEqual(p.lastname, None)
