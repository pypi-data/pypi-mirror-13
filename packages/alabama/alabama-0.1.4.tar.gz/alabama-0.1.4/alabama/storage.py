from query import Query
from models import generate_id
import connection


def insert(instance):
    values = instance.to_json() 
    q, v = Query(instance.__class__).values(values).insert()
    connection.my_connection().execute(q, v)
    return True


def delete(cls, args=None, uuid=None):
    args = args or {}
    if uuid:
        args['uuid'] = uuid
    sql, values = Query(cls).where(args).delete()
    connection.my_connection().execute(sql, values)
    return True


def put(instance):
    if not instance.uuid:
        instance.uuid = generate_id()
        insert(instance)
        return instance

    if not exist(instance.__class__, uuid=instance.uuid):
        insert(instance)
        return instance

    update(instance, {'uuid': instance.uuid})
    return instance


def find(cls, limit=1000, where=None, order="", operator_where=Query.AND):
    where = where or {}
    q = Query(cls).select('*')
    deleted_keys = []

    for key in where:
        values = where[key]

        # example of usages:
        # .find(Person, where={'code_language': (Query.IN, ['ruby', 'python']))
        if isinstance(values, tuple):
            val = values[1]
            if isinstance(values[1], list):
                val = tuple(values[1])
            q = q.where({key: val}, values[0])
            deleted_keys.append(key)

    for key in deleted_keys:
        del where[key]

    q.where(where, operator_where=operator_where).limit(limit).order(order)
    result = query(q)
    if cls.__name__ in result:
        return result[cls.__name__]
    return []


def exist(cls, where=None, uuid=None):
    where = where or {}
    if uuid:
        where['uuid'] = uuid

    q = Query(cls).select(["count(*)"]).where(where).limit(1)
    sql, where = q.query()
    connection.my_connection().execute(sql, where)
    results = connection.my_connection().fetchall()
    return results[0][0] > 0


def get_all(cls, uuids=None, limit=30):
    uuids = uuids or []
    q = Query(cls).select('*')\
                  .where({'uuid': tuple(uuids)}, Query.IN)\
                  .limit(limit)
    r = query(q)
    if cls.__name__ in r:
        return r[cls.__name__]
    return []


def get(cls, where=None, uuid=None):
    where = where or {}
    if uuid:
        where['uuid'] = uuid

    rets = find(cls, 1, where)
    if len(rets):
        return rets[0]
    return None


def update(instance, where=None):
    where = where or {}
    values = instance.to_json()
    q, v = Query(instance.__class__).values(values).where(where).update()
    connection.my_connection().execute(q, v)
    return True


def query(query):
    sql, args = query.query()
    connection.my_connection().execute(sql, args)
    results = connection.my_connection().fetchall()
    class_with_fields = query.split_select(connection.my_connection().description())
    return __objects_resulted_from_join(results, class_with_fields)


def create_database(models):
    if not isinstance(models, list):
        models = [models]

    all_queries = ""
    for table in models:
        all_queries += table.create_table_sql()

    connection.my_connection().execute(all_queries)


def __objects_resulted_from_join(results, fields_of_class):
    ret = dict()
    for result in results:
        for cls in fields_of_class.keys():

            obj = cls()
            obj = __clean_properties(obj)

            for field_name in fields_of_class[cls]:
                value = result[field_name[1]]
                if value and isinstance(value, str):
                    value = value.strip()
                setattr(obj, field_name[0], value)

            if cls.__name__ in ret:
                ret[cls.__name__].append(obj)
            else:
                ret[cls.__name__] = [obj]
    return ret


def __clean_properties(instance):
    for prop in instance.to_json():
        setattr(instance, str(prop), None)

    return instance
