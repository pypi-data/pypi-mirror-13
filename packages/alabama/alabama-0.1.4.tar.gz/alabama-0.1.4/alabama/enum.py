
def frozen():
    def set_attr(self, name, value):
        raise AttributeError("You cannot add attributes to %s" % self)
    return set_attr


class Enum(object):
    __setattr__ = frozen()

    class __metaclass__(type):
        __setattr__ = frozen()

    @classmethod
    def to_value(cls, key):
        if hasattr(cls, key):
            return getattr(cls, key)
        raise Exception("%s doesnt have the key: %s" % (cls.__name__, key))

    @classmethod
    def keys_values(cls):
        keys_and_values = {}

        for prop in cls.__dict__:
            if not prop.startswith('_') and \
               not isinstance(cls.__dict__[prop], staticmethod):
                keys_and_values[str(prop)] = cls.__dict__[prop]

        return keys_and_values

    @classmethod
    def values(cls):
        all_values = []

        for i in cls.__dict__:
            if not i.startswith('_') and \
               not isinstance(cls.__dict__[i], staticmethod):
                all_values.append(cls.__dict__[i])

        return all_values

    @classmethod
    def exist(cls, property):
        all_properties = cls.keys_values()
        return property in all_properties
