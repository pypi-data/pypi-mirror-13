import unittest
import connection
from models import BaseModel, StringProperty, IntegerProperty, FloatProperty, EnumProperty, BooleanProperty
from enum import Enum


class Age(BaseModel):
    name = StringProperty()
    age = FloatProperty()

    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age


class Gender(Enum):
    male = "male"
    famale = 'female'


class Person(BaseModel):
    active = BooleanProperty()
    name = StringProperty()
    lastname = StringProperty(140)
    age = IntegerProperty()
    weight = FloatProperty()
    gender = EnumProperty(Gender)

    def __init__(self, name=None, lastname=None, age=10, weight=23):
        self.name = name
        self.lastname = lastname
        self.age = age
        self.weight = weight


class TestLoader(unittest.TestCase):

    def setUp(self):
        database = connection.start_db('tests/db.properties')
        connection.create_pool(database)
        sql = 'CREATE TABLE ' + Age.table_name() \
              + ' (name varchar, age int, uuid varchar);'

        sql += 'CREATE TABLE ' + Person.table_name() + \
               ' (name varchar, lastname varchar, active boolean, \
               age int, weight int, uuid varchar, gender varchar)'
        execute(sql)

    def tearDown(self):
        sql = 'DROP TABLE ' + Age.table_name() + ';'
        sql += 'DROP TABLE ' + Person.table_name() + ';'
        execute(sql)


def clear():
    connection.my_connection().execute("SELECT t.table_name FROM "
                                       "information_schema.tables "
                                       "t where t.table_schema = 'public'")

    result = connection.my_connection().fetchall()
    sql = ""
    for i in result:
        sql += "TRUNCATE " + i[0] + " CASCADE;"

    connection.my_connection().execute(sql)


def reset():
    try:
        clear()
    finally:
        connection.my_connection().close()


def execute(sql):
    try:
        connection.my_connection().execute(sql)
    except Exception as e:
        print(e)
    finally:
        connection.my_connection().close()
