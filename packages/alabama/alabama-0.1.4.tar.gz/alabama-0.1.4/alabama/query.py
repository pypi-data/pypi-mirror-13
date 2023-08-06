from collections import OrderedDict


class BadFormedQuery(Exception):
    pass


class Query(object):
    EQUAL = "="
    NOT_EQUAL = "!="
    IN = " IN "
    NOT_IN = " NOT IN "
    BIGGER_THAN = " > "
    LOWER_THAN = " < "
    LIKE = " LIKE "
    OR = " OR "
    AND = " AND "

    def __init__(self, cls, alias=None):
        self.base_table = cls.table_name()
        self.selects = None
        self.join_query = ""
        self.wheres = None
        self.query_str = None
        self.select_text = None
        self.limit_select = 1000
        self.params_where = []
        self.params_values = []
        self.param_custom_where = None
        self.order_by = None
        self.operator_where = None

        if not alias:
            self.tables_used = {'default': cls}
            return

        self.tables_used = {alias: cls}
        self.base_table = self.base_table + ' ' + alias

    def select(self, selects):
        self.select_text = ''
        if not isinstance(selects, list):
            selects = [selects]
        self.selects = selects
        for i in selects:
            self.select_text += i + ','
        self.select_text = self.select_text[:-1]
        return self

    def join(self, instance, alias=None, on=None):
        if not alias or not on:
            raise BadFormedQuery('Alias and on need be informed')

        if 'default' in self.tables_used:
            raise BadFormedQuery('Main table must have alias')

        self.tables_used[alias] = instance
        self.join_query += ' JOIN ' + instance.table_name()
        self.join_query += ' ' + alias + ' ON ' + on
        return self

    def split_select(self, columns=None):
        cls_fields = OrderedDict()

        if len(self.selects) < 2:

            sel = self.selects[0]
            if '*' in sel:

                alias = 'default'
                if '.' in sel:
                    alias = sel.split('.')[0]

                cls = self.tables_used[alias]
                cls_fields[cls] = []

                for i, column in enumerate(columns):
                    cls_fields[cls].append((column, i))

                return cls_fields

        count = 0

        for sel in self.selects:
            alias, field_name = sel.split('.')
            cls = self.tables_used[alias]

            if cls in cls_fields:
                cls_fields[cls].append((field_name, count))
            else:
                cls_fields[cls] = [(field_name, count)]

            count += 1

        return cls_fields

    def where(self, params_where, operator=EQUAL, operator_where=AND):
        self.operator_where = operator_where
        self.params_where.append((params_where, operator))
        return self

    def values(self, params_values):
        self.params_values = params_values
        return self

    def split_values(self):
        if not self.params_values:
            return None
        return self.params_values.values()

    def split_where(self):
        values = []
        for params, _ in self.params_where:
            values.extend(params.values())
        return values

    def limit(self, lim):
        if lim:
            self.limit_select = lim
        return self

    def delete(self):
        query = 'DELETE FROM %s' % self.base_table

        if len(self.params_where) > 0:
            query += self.__where()
        return query, self.split_where()

    def order(self, order_by):
        self.order_by = order_by
        return self

    def update(self):
        query = 'UPDATE %s' % self.base_table

        if self.params_values:
            values_str = Query.__join_values(self.params_values, "=", ',')
            values_str = values_str[1:]
            query += ' SET ' + values_str

        if len(self.params_where) > 0:
            query += self.__where()

        values = self.split_values()
        where = self.split_where()
        if where:
            values.extend(where)
        return query, values

    def insert(self):
        query = 'INSERT INTO %s (' % self.base_table
        query += self.__info_separator(self.params_values, ',') + ')'
        query += ' VALUES ('
        values = []
        for _ in self.params_values:
            values.append('%s')
        query += self.__info_separator(values, ',') + ')'
        return query, self.split_values()

    def query(self):
        if self.select_text:
            self.query_str = 'SELECT ' + \
                             self.select_text + ' FROM ' + self.base_table
        if self.join_query:
            self.query_str += self.join_query

        if len(self.params_where) > 0:
            self.query_str += self.__where()

        if self.order_by:
            self.query_str += ' ORDER BY ' + self.order_by

        if self.select_text:
            self.query_str += ' LIMIT ' + str(self.limit_select)

        return self.query_str, self.split_where()

    def __where(self):
        query = ""
        for params, operator in self.params_where:
            query += self.__join_values(params, operator,
                                        self.operator_where)

        if any(query):
            pos = len(self.operator_where)
            query = query[pos:]
            query = Query.AND + query
        return ' WHERE 1=1' + query

    @staticmethod
    def __info_separator(values, separator):
        ret = ''
        for i in values:
            ret += i + separator
        ret = ret[:-1]
        return ret

    @staticmethod
    def __igual_separator(values, separator):
        value = ''
        for i in values:
            value += separator + i + '= %s'
        return value

    @staticmethod
    def __join_values(values, operator, separator):
        value = ''
        for key in values:
            value += separator + key + operator + '%s'
        return value
