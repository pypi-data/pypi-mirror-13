import os


class Properties(object):

    def __init__(self, path):
        self.__props = {}
        full_path = os.path.abspath(path)

        if not os.path.isfile(full_path):
            full_path = os.path.abspath(path)

        self.__read_file(full_path)

    def __read_file(self, full_path):
        with open(full_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key, value = line.split('=')
                self.__props[key] = value

    def key(self, key, default=None):
        if key in self.__props:
            return self.__props[key]
        return default

    def key_int(self, key, default=None):
        value = self.key(key, default)
        if value:
            return int(value)
        return default

    def key_bool(self, key, default=None):
        value = self.key(key, default)
        if value:
            return value == "True"
        return default
