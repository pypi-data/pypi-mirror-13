from test_connection_db import TestLoader
from mock import Age, Person
import storage
import connection
from storage import Query


class TestDatabaseAPIUsage(TestLoader):
    
    def test_insert(self):
        self.assertTrue(storage.insert(Age('mouse', 20)))
        test_obj = storage.find(Age)
        self.assertEqual(test_obj[0].name, 'mouse')
        self.assertEqual(test_obj[0].age, 20)
        self.assertIsNotNone(test_obj)

    def test_select(self):
        for i in range(0, 2):
            self.assertTrue(storage.insert(Age('mouse', 20)))

        test_obj = storage.find(Age)
        self.assertEqual(len(test_obj), 2)

    def test_select_one(self):
        for i in range(20, 22):
            name = 'mouse %s' % (i)
            self.assertTrue(storage.insert(Age(name, i)))

        test_obj = storage.find(Age, limit=1,
                                where={'age': 20, 'name': 'mouse 20'})

        self.assertEqual(1, len(test_obj))
        self.assertTrue(isinstance(test_obj[0], Age))
        self.assertEqual(test_obj[0].name, 'mouse 20')
        self.assertEqual(test_obj[0].age, 20)

    def test_select_limit(self):
        for i in range(20, 23):
            self.assertTrue(storage.insert(Age('mouse', i)))

        result = storage.find(Age, limit=1)
        self.assertEqual(1, len(result))

    def test_select_in(self):
        for i in range(20, 23):
            self.assertTrue(storage.insert(Age('mouse', i)))

        result = storage.find(Age, where={'age': (Query.IN, [20, 21, 23])})
        self.assertEqual(2, len(result))

    def test_delete(self):
        storage.insert(Age('mouse', 20))
        storage.delete(Age)

        saved_objects = storage.find(Age)
        self.assertEqual(len(saved_objects), 0)

        model = storage.put(Person(name='alabama'))
        storage.put(Person(name='orm'))
        storage.delete(Person, uuid=model.uuid)

        saved_objects = storage.find(Person)
        self.assertEqual(len(saved_objects), 1)

    def test_update_all(self):
        for i in range(10, 50, 10):
            self.assertTrue(storage.insert(Age('mouse', i)))

        self.assertTrue(storage.update(Age('mouse', 50)))
        test_obj = storage.find(Age, limit=10, where={'age': 50, 'name': 'mouse'})

        self.assertEqual(4, len(test_obj))
        self.assertTrue(isinstance(test_obj[0], Age))

        self.assertEqual(test_obj[0].name, 'mouse')
        self.assertEqual(test_obj[0].age, 50)

    def test_update(self):
        for i in range(10, 50, 10):
            self.assertTrue(storage.insert(Age('mouse', i)))

        self.assertTrue(storage.update(Age('mouseUpdated', 50),
                        where={'age': 10, 'name': 'mouse'}))

        test_obj = storage.find(Age, limit=10,
                                where={'age': 50, 'name': 'mouseUpdated'})

        self.assertEqual(1, len(test_obj))
        self.assertTrue(isinstance(test_obj[0], Age))
        self.assertEqual(test_obj[0].name, 'mouseUpdated')
        self.assertEqual(test_obj[0].age, 50)

    def test_query(self):
        storage.insert(Age('mouse', 22))
        storage.insert(Person('mouse', 'mickey', 23, 22.2))
        storage.insert(Person('mouse', 'minnie', 23, 22.2))

        q = Query(Person, alias='p').select(['p.age', 'a.age', 'p.lastname']) \
                                    .join(Age, alias='a', on='a.name = p.name') \
                                    .where({'p.lastname': 'mickey', 'a.age': 22})

        r = ('SELECT p.age,a.age,p.lastname FROM tb_Person p '
             'JOIN tb_Age a ON a.name = p.name WHERE 1=1 AND '
             'p.lastname=%s AND a.age=%s LIMIT 1000', ['mickey', 22])
        self.assertEqual(r, q.query())

        objects = storage.query(q)
        self.assertEqual(len(objects), 2)
        age, person = objects['Age'][0], objects['Person'][0]

        self.assertEqual(person.age, 23)
        self.assertEqual(person.lastname, 'mickey')
        self.assertEqual(age.age, 22)

        q = Query(Person, alias='p')\
            .select(['p.*'])\
            .join(Age, alias='a', on='a.name = p.name')\
            .where({'p.lastname': 'mickey', 'a.age': 22})

        r = ('SELECT p.* FROM tb_Person p JOIN tb_Age a ON a.name = '
             'p.name WHERE 1=1 AND p.lastname=%s AND '
             'a.age=%s LIMIT 1000', ['mickey', 22])
        self.assertEqual(r, q.query())

        objects = storage.query(q)
        self.assertEqual(len(objects), 1)
        person = objects['Person'][0]

        self.assertEqual(person.age, 23)
        self.assertEqual(person.lastname, 'mickey')

    def test_query_in(self):
        storage.insert(Age('mouse', 22))
        storage.insert(Person('mouse', 'mickey', 23, 22.2))
        storage.insert(Person('mouse', 'minnie', 23, 22.2))

        q = Query(Person).select(["*"])\
                         .where({'lastname': ('mickey', 'minnie')}, Query.IN)
        a = storage.query(q)
        self.assertEqual(len(a[Person.__name__]), 2)

    def test_put(self):
        p = Person('philip', 'folk', 20)
        self.assertIsNone(p.uuid)
        p = storage.put(p)
        self.assertIsNotNone(p.uuid)

        p.name = 'petter'
        new_p = storage.put(p)
        self.assertEqual(new_p.uuid, p.uuid)

    def test_query_get_all(self):
        uuids = []
        uuids.append(storage.put(Person('mouse1', 'minnie1', 23, 22.2)).uuid)
        uuids.append(storage.put(Person('mouse2', 'minnie2', 23, 22.2)).uuid)
        uuids.append(storage.put(Person('mouse3', 'minnie3', 23, 22.2)).uuid)
        uuids.append(storage.put(Person('mouse4', 'minnie4', 23, 22.2)).uuid)
        persons = storage.get_all(Person, uuids)
        self.assertEquals(len(persons), 4)

    def test_join(self):
        storage.put(Age(name='alabama'))
        storage.put(Person(name='alabama', lastname='felipe'))
        storage.put(Person(name='alabama', lastname='alabama'))

        query = Query(Person, alias='p').select(['p.*'])\
                                        .join(Age, alias='a', on='p.name = a.name')\
                                        .where({'p.name': 'alabama'})\
                                        .order("p.lastname DESC")

        results = storage.query(query)
        self.assertEqual(1, len(results))
        self.assertEqual('felipe', results['Person'][0].lastname)
        self.assertTrue('Person' in results)
        self.assertIsNotNone(results['Person'])

    def test_get(self):
        person = storage.put(Person(name='alabama'))

        person_from_db = storage.get(Person, uuid=person.uuid)
        self.assertEqual(person.name, person_from_db.name)
        self.assertEqual(person.uuid, person_from_db.uuid)


class TestStorageCreateDatabase(TestLoader):

    @connection.transaction
    def create_db_just_person(self):
        storage.create_database(Person)

    @connection.transaction
    def create_db(self):
        storage.create_database([Person, Age])

    @connection.transaction
    def drop_person(self):
        sql = 'DROP TABLE tb_Person;'
        connection.my_connection().execute(sql)

    @connection.transaction
    def drop_all(self):
        sql = 'DROP TABLE tb_Person; DROP TABLE tb_Age;'
        connection.my_connection().execute(sql)

    def test_create_database(self):
        self.drop_person()
        self.create_db_just_person()
        self.assertEqual(0, len(storage.find(Person)))

        self.drop_all()
        self.create_db()
        self.assertEqual(0, len(storage.find(Person)))
        self.assertEqual(0, len(storage.find(Age)))
