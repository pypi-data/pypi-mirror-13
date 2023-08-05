import inspect
import uuid
from properties import Properties


class PostgreSQLTypes(object):
    char = 'CHAR'
    boolean = 'BOOLEAN'
    int = 'INT'
    bigint = 'BIGINT'
    real = 'real'


class BaseProperty(object):
    def __init__(self):
        pass

    def __get__(self, obj, objtype=None):
        if not obj:
            return self

        if self.property_name not in obj.__dict__:
            obj.__dict__[self.property_name] = None

        return obj.__dict__[self.property_name]

    def __set__(self, obj, value):
        self._validate(value)
        obj.__dict__[self.property_name] = value

    def _validate(self, value):
        pass

    def _type(self):
        raise NotImplementedError


class StringProperty(BaseProperty):

    def __init__(self, size=512):
        self._size = size

    def _validate(self, value):
        if value and not (isinstance(value, str)):
            raise ValueError("The value " + self.property_name +
                             " must be a string, but was: " + str(value))

    def _type(self):
        return '%s(%s)' % (PostgreSQLTypes.char, self._size)


class BooleanProperty(BaseProperty):

    def _validate(self, value):
        if value and not (isinstance(value, bool)):
            raise ValueError("The value must be bool")

    def _type(self):
        return PostgreSQLTypes.boolean


class EnumProperty(BaseProperty):

    def __init__(self, cls):
        self.enum_type = cls

    def _validate(self, value):
        if value and not self.enum_type.exist(value):
            raise ValueError("This EnumProperty:" + value +
                             " is not valid to EnumType:" +
                             self.enum_type.__name__)

    def _type(self):
        typeof = type(self.enum_type.values()[0]).__name__
        return {'str': PostgreSQLTypes.char, 'int': PostgreSQLTypes.int}[typeof]


class IntegerProperty(BaseProperty):
    def _validate(self, value):
        if value and not (isinstance(value, int) or isinstance(value, long)):
            raise ValueError("The value " +
                             self.property_name + " must be a integer")

    def _type(self):
        return PostgreSQLTypes.int


class BigIntegerProperty(IntegerProperty):

    def _type(self):
        return PostgreSQLTypes.bigint


class FloatProperty(BaseProperty):

    def _type(self):
        return PostgreSQLTypes.real


class ModelBasicProtocol(type):

    @staticmethod
    def _descript_class(attributes):
        description = dict()
        for i in attributes:
            if isinstance(attributes[i], BaseProperty):
                attributes[i].property_name = i
                description[i] = attributes[i]

        return description

    def __new__(cls, name, parents, dct):
        description = dict()
        for parent in parents:
            desc = ModelBasicProtocol._descript_class(parent.__dict__)
            description.update(desc)

        description.update(ModelBasicProtocol._descript_class(dct))
        dct["_prop_desc"] = description

        if '__init__' in dct:
            init_fun = dct['__init__']
            init_inspection = inspect.getargspec(init_fun)
            if init_inspection.defaults is None \
               and len(init_inspection.args) > 1:
                raise Exception('A modelobject must have '
                                'a keywords arguments in __init__')

        return type.__new__(cls, name, parents, dct)


def generate_id():
    return uuid.uuid4().hex


class BaseModel(object):
    __metaclass__ = ModelBasicProtocol

    uuid = StringProperty()

    def __init__(self, *args, **kargs):
        for k, value in kargs.items():
            if k in dir(self):
                setattr(self, k, value)

    def to_json(self):
        return_json = {}

        for key, _ in sorted(self._prop_desc.items()):
            if key in self.__dict__:

                value = self.__dict__[key]
                if not isinstance(value, Properties):
                    return_json[key] = value

        return return_json

    @classmethod
    def to_instance(cls, json):
        return cls(**json)

    @classmethod
    def create_table_sql(cls):
        uuid = "uuid %s(36) PRIMARY KEY," % (PostgreSQLTypes.char)
        fields = ""

        for prop, prop_type in sorted(cls._prop_desc.items()):
            if prop == 'uuid':
                continue

            fields += "%s %s, " % (prop, prop_type._type())

        fields = fields[0:-2]

        return "CREATE TABLE tb_%s (%s %s);" % (cls.__name__, uuid, fields)
