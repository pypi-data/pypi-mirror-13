import inspect
import uuid
from properties import Properties
from weakref import WeakKeyDictionary


class PostgreSQLTypes(object):
    char = 'CHAR'
    boolean = 'BOOLEAN'
    int = 'INT'
    bigint = 'BIGINT'
    real = 'real'


def make_this_descriptor(desc_class):
    desc_class.__get__ = dunder_get
    desc_class.__set__ = dunder_set
    return desc_class


def dunder_get(self, instance, instancetype):
    return self.data.get(instance, self.value)


def dunder_set(self, instance, new_value):
    self._validate(new_value)
    self.data[instance] = new_value


class BaseProperty(object):

    def __init__(self):
        self.property_name = self.__class__.__name__
        self.data = WeakKeyDictionary()
        self.value = None

    def _validate(self, value):
        pass

    def _type(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self.__class__)


@make_this_descriptor
class StringProperty(BaseProperty):

    def __init__(self, size=512):
        super(StringProperty, self).__init__()
        self._size = size

    def _validate(self, value):
        if value and not (isinstance(value, basestring)):
            raise ValueError("The value " + self.property_name +
                             " must be a string, but was: " + str(value))

    def _type(self):
        return '%s(%s)' % (PostgreSQLTypes.char, self._size)


@make_this_descriptor
class BooleanProperty(BaseProperty):

    def _validate(self, value):
        if value and not (isinstance(value, bool)):
            raise ValueError("The value must be bool")

    def _type(self):
        return PostgreSQLTypes.boolean


@make_this_descriptor
class EnumProperty(BaseProperty):

    def __init__(self, cls):
        super(EnumProperty, self).__init__()
        self.enum_type = cls

    def _validate(self, value):
        if value and not self.enum_type.exist(value):
            raise ValueError("This EnumProperty:" + value +
                             " is not valid to EnumType:" +
                             self.enum_type.__name__)

    def _type(self):
        typeof = type(self.enum_type.values()[0]).__name__
        return {'str': PostgreSQLTypes.char, 'int': PostgreSQLTypes.int}[typeof]


@make_this_descriptor
class IntegerProperty(BaseProperty):
    def _validate(self, value):
        if value and not (isinstance(value, int) or isinstance(value, long)):
            raise ValueError("The value " +
                             self.property_name + " must be a integer")

    def _type(self):
        return PostgreSQLTypes.int


@make_this_descriptor
class BigIntegerProperty(IntegerProperty):

    def _type(self):
        return PostgreSQLTypes.bigint


@make_this_descriptor
class FloatProperty(BaseProperty):

    def _type(self):
        return PostgreSQLTypes.real


class ModelBasicProtocol(type):

    @staticmethod
    def _mount_property_details(class_dict):
        description = {}

        for attribute in class_dict:
            if isinstance(class_dict[attribute], BaseProperty):
                # set the name of the column to the column object
                class_dict[attribute].property_name = attribute
                description[attribute] = class_dict[attribute]

        return description

    def __new__(cls, name, parents, dct):
        description = {}
        # add to _properties_details all properties that the classes
        # that this Property inherity.
        for parent in parents:
            desc = ModelBasicProtocol._mount_property_details(parent.__dict__)
            description.update(desc)

        # add to _properties_details all properties that this class has
        description.update(ModelBasicProtocol._mount_property_details(dct))

        dct["_properties_details"] = description

        if '__init__' in dct:
            init_method = dct['__init__']
            init_inspection = inspect.getargspec(init_method)

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
        all_attributes = dir(self)

        for key, _ in sorted(self._properties_details.items()):
            if key in all_attributes: 
                value = getattr(self, key)
                #if not isinstance(value, Properties):
                return_json[key] = value

        return return_json

    @classmethod
    def to_instance(cls, json):
        return cls(**json)

    @classmethod
    def table_name(cls):
        return 'tb_%s' % (cls.__name__,)

    @classmethod
    def columns(cls):
        return [column_name for column_name, column_class in sorted(cls._properties_details.items())]

    @classmethod
    def create_table_sql(cls):
        uuid = "uuid %s(36) PRIMARY KEY," % (PostgreSQLTypes.char)
        fields = ""

        for prop, prop_type in sorted(cls._properties_details.items()):
            if prop == 'uuid':
                continue

            fields += "%s %s, " % (prop, prop_type._type())

        fields = fields[0:-2]

        return "CREATE TABLE %s (%s %s);" % (cls.table_name(), uuid, fields,)
