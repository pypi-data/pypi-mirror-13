import threading
import properties
from collections import namedtuple
from functools import wraps
from psycopg2.pool import ThreadedConnectionPool


_pool = None
_local = threading.local()

DatabasePropertiesClass = namedtuple('DatabaseProperties', 'name user password host show_sql')


def __read_db_properties(filepath):
    props = properties.Properties(filepath)

    DBNAME = props.key('db.name')
    USER = props.key('db.user')
    PASSWORD = props.key('db.password')
    HOST = props.key('db.host')
    SHOW_SQL = props.key_bool('db.show_sql')

    return DatabasePropertiesClass(name=DBNAME, user=USER, password=PASSWORD, host=HOST, show_sql=SHOW_SQL)


def start_db(dbproperties_filepath):
    return __read_db_properties(dbproperties_filepath)


def create_pool(database):
    global _pool
    _pool = ThreadedConnectionPool(1, 20, dbname=database.name, user=database.user,
                                   host=database.host, password=database.password)
    _pool.show_sql = database.show_sql


def _requires_local():
    if not hasattr(_local, 'connection'):
        _local.connection = None
    return _local


class TransactionalControl(object):
    def __enter__(self):
        pass

    def __exit__(self, error, value, traceback):
        connection = _requires_local().connection
        if connection:
            if error:
                connection.rollback()
            else:
                connection.commit()

        if error:
            raise value


def transaction(fnc):
    @wraps(fnc)
    def inner(*args, **kwargs):
        with TransactionalControl():
            fnc(*args, **kwargs)
    return inner


def my_connection():
    local = _requires_local()
    if not local.connection:
        local.connection = DatabaseConnection()
    return local.connection


def close():
    if not _local.connection:
        _local.connection.close()
        _local.connection = None


class DatabaseConnection(object):

    def __init__(self):
        self.cur = None
        self.connection = None

    def execute(self, query, values=None):
        cur = self.__cursor()
        self.__log_sql(cur, query, values)
        if values:
            cur.execute(query, values)
        else:
            cur.execute(query)
        return self

    def close(self):
        if self.cur:
            self.commit()
            if not self.cur.closed:
                self.cur.close()

    def commit(self):
        if self.connection:
            self.connection.commit()
            _pool.putconn(self.connection)
            self.connection = None

    def rollback(self):
        if self.connection:
            self.connection.rollback()
            if not self.cur.closed:
                self.cur.close()
            _pool.putconn(self.connection)
            self.connection = None

    def fetchall(self):
        if self.cur:
            return self.cur.fetchall()
        raise ConnException("No cursor to fetch")

    def description(self):
        if self.cur:
            columns = [column.name for column in self.cur.description]
            return columns
        return []

    @staticmethod
    def __log_sql(cur, query, values):
        global _pool
        if _pool.show_sql:
            print(cur.mogrify(query, values))

    def __cursor(self):
        global _pool
        if not self.connection:
            self.connection = _pool.getconn()

        if self.cur:
            if not self.cur.closed:
                self.cur.close()
        self.cur = self.connection.cursor()

        return self.cur


class ConnException(Exception):
    pass
