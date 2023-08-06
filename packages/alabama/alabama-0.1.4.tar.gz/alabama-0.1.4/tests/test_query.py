import unittest
from storage import Query
from mock import Age, Person


class TestQuerys(unittest.TestCase):

    def test_insert_query(self):
        sql = Query(Age).values({'name': 'mouse', 'age': 22.5}).insert()
        self.assertEqual("INSERT INTO " + Age.table_name() + " (age,name) VALUES (%s,%s)", sql[0])
        self.assertEqual([22.5, 'mouse'], sql[1])

    def test_select_query(self):
        result = ("SELECT * FROM " + Age.table_name() + " WHERE 1=1 AND name=%s LIMIT 30", ['mickey'])
        query = Query(Age).select(['*']).where({"name": 'mickey'}).limit(30).query()
        self.assertEqual(result, query)

        result = ("SELECT * FROM " + Age.table_name() + "\
 WHERE 1=1 AND age=%s AND name=%s LIMIT 30", [20, 'mickey'])
        query = Query(Age).select(['*']).where({"age": 20, "name": 'mickey'}).limit(30).query()
        self.assertEqual(result, query)

        result = ("SELECT * FROM " + Age.table_name() + " \
WHERE 1=1 AND age=%s OR name=%s LIMIT 30", [20, 'mickey'])
        query = Query(Age).select(['*']).where({"age": 20, "name": 'mickey'}, operator_where=Query.OR).limit(30).query()
        self.assertEqual(result, query)

        result = ("SELECT * FROM " + Age.table_name() + " WHERE 1=1 AND name=%s LIMIT 1", ['mickey'])
        query = Query(Age).select(['*']).where({"name": 'mickey'}).limit(1).query()
        self.assertEqual(result, query)

        result = ("SELECT * FROM " + Age.table_name() + " LIMIT 1", [])
        query = Query(Age).select(['*']).limit(1).query()
        self.assertEqual(result, query)

        result = ("SELECT a.name FROM " + Age.table_name() + " a WHERE 1=1 AND a.name=%s LIMIT 1", ['mickey'])
        query = Query(Age, "a").select(['a.name']).where({"a.name": 'mickey'}).limit(1).query()
        self.assertEqual(result, query)

    def test_select_join_query(self):
        q = Query(Person, alias='p').select(['a.age', 'p.lastname']) \
                                    .join(Age, alias='a', on='a.name = p.name') \
                                    .where({'p.lastname': 'mickey', 'a.age': 22})

        r = ('SELECT a.age,p.lastname FROM tb_Person p JOIN tb_Age a \
ON a.name = p.name WHERE 1=1 AND p.lastname=%s AND a.age=%s LIMIT 1000', ['mickey', 22])
        self.assertEqual(r, q.query())

    def test_select_where_compost(self):
        q = Query(Person, alias='p').select(['a.age', 'p.lastname']) \
                                    .where({'p.lastname': 'mickey', 'a.age': 22}) \
                                    .where({'p.lastname': 'mouse'}, Query.NOT_EQUAL)

        r = ('SELECT a.age,p.lastname FROM tb_Person p WHERE 1=1 AND p.lastname=%s \
AND a.age=%s AND p.lastname!=%s LIMIT 1000', ['mickey', 22, 'mouse'])
        self.assertEqual(r, q.query())

    def test_delete(self):
        q = Query(Age).delete()
        r = ("DELETE FROM " + Age.table_name(), [])
        self.assertEqual(q, r)

        q = Query(Age).where({'name': 'mouse'}).delete()
        r = ("DELETE FROM " + Age.table_name() + " WHERE 1=1 AND name=%s", ['mouse'])
        self.assertEqual(q, r)

        q = Query(Age).where({'name': 'mouse', 'age': 20}).delete()
        r = ("DELETE FROM " + Age.table_name() + " WHERE 1=1 AND age=%s AND name=%s", [20, 'mouse'])
        self.assertEqual(q, r)

    def test_update(self):
        q = Query(Age).values({"age": 22, "name": "minnie"}).where({"age": 20, "name": "mickey"}).update()
        r = ("UPDATE " + Age.table_name() + " SET age=%s,name=%s \
WHERE 1=1 AND age=%s AND name=%s", [22, "minnie", 20, "mickey"])
        self.assertEqual(q, r)

        q = Query(Age).values({"age": 22, "name": "minnie"}).update()
        r = ("UPDATE " + Age.table_name() + " SET age=%s,name=%s", [22, "minnie"])
        self.assertEqual(q, r)
