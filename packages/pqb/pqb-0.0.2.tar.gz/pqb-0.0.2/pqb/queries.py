from . import statements
from . import grouping
from . import expressions
import json

class Select:
    def __init__(self, *args):
        super(self.__class__, self).__init__()
        self.raw_fields = args
        self.raw_fields = []
        self.raw_fields_group = []
        self.fields = []
        self.group_fields = []
        self.raw_tables = []
        self.raw_order_by = []
        self.order_by_fields = []
        self.tables = []
        self.where_criteria = grouping.ConditionalGrouping()

    def prepareData(self):
        if isinstance(self.raw_fields, str):
            self.raw_fields = self.raw_fields.split(',')

        for x in self.raw_fields:
            self.fields.append(expressions.AliasExpression(x).result())
        
        if len(self.fields) == 0:
            self.fields.append('*')

        for x in self.raw_tables:
            self.tables.append(expressions.AliasExpression(x).result())

        if isinstance(self.raw_fields_group, str):
            self.raw_fields_group = self.raw_fields_group.split(',')


        for x in self.raw_fields_group:
            self.group_fields.append(expressions.AliasExpression(x).result())


        if isinstance(self.raw_order_by, str):
            self.raw_order_by = self.raw_order_by.split(',')

        for x in self.raw_order_by:
            self.order_by_fields.append(expressions.OrderByExpression(*x).result())

    def from_(self, table, alias=None):
        if isinstance(table, str):
            table = [[table, alias]]
        self.raw_tables = table
        return self

    def where(self, field, value = None, operator = None):
        conjunction = None
        if value is None and isinstance(field, dict):
            for f,v in field.items():
                if len(self.where_criteria) > 0:
                    conjunction = 'AND'
                self.where_criteria.append(expressions.ConditionExpression(f, v, operator=operator, conjunction=conjunction))
                
        else:
            if len(self.where_criteria) > 0:
                    conjunction = 'AND'
            self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def where_or(self, field, value, operator = None):
        conjunction = None
        if len(self.where_criteria) > 0:
            conjunction = 'OR'
        self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def group_by(self, *args):
        if len(args) == 1:
            self.raw_fields_group = args[0].split(',')
        else:
            self.raw_fields_group = list(args)
        return self

    def order_by(self, field, orientation='ASC'):
        if isinstance(field, list):
            self.raw_order_by.append(field)
        else:
            self.raw_order_by.append([field, orientation])

        return self

    def result(self, *args, **kwargs):
        prettify = kwargs.get('pretty', False)
        self.prepareData()
        sql = 'SELECT '

        sql +=  ', '.join(self.fields)
        

        if len(self.tables) > 0:
            if prettify:
                sql += '\n'
            else:
                sql += ' '
            sql +=  'FROM '
            sql +=  ', '.join(self.tables)
        if len(self.where_criteria) > 0:
            if prettify:
                sql += '\n'
            else:
                sql += ' '
            sql +=  'WHERE '
            sql +=  self.where_criteria.result()
        if len(self.group_fields) > 0:
            if prettify:
                sql += '\n'
            else:
                sql += ' '
            sql +=  'GROUP BY '
            sql +=  ', '.join(self.group_fields)
        if len(self.order_by_fields) > 0:
            if prettify:
                sql += '\n'
            else:
                sql += ' '
            sql +=  'ORDER BY '
            sql +=  ', '.join(self.order_by_fields)
            if prettify:
                sql += '\n'
            else:
                sql += ' '
        
        return sql

class Delete(object):
    _class = None
    _cluster = None
    _type = None
    data = {}
    where_criteria = grouping.ConditionalGrouping()

    def __init__(self, type):
        super(Delete, self).__init__()
        self._type = type
    
    def class_(self, _class):
        self._class = _class
        return self
        
    def where(self, field, value = None, operator = None):
        conjunction = None
        if value is None and isinstance(field, dict):
            for f,v in field.items():
                if len(self.where_criteria) > 0:
                    conjunction = 'AND'
                self.where_criteria.append(expressions.ConditionExpression(f, v, operator=operator, conjunction=conjunction))
                
        else:
            if len(self.where_criteria) > 0:
                    conjunction = 'AND'
            self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def where_or(self, field, value, operator = None):
        conjunction = None
        if len(self.where_criteria) > 0:
            conjunction = 'OR'
        self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def result(self, *args, **kwargs):
        prettify = kwargs.get('pretty', False)

        sql = 'DELETE %s %s' % (self._type, self._class)
        
        if prettify:
            sql += '\n'
        else:
            sql += ' '

        if len(self.where_criteria) > 0:
            sql +=  'WHERE '
            sql +=  self.where_criteria.result()
            if prettify:
                sql += '\n'
            else:
                sql += ' '
        
        return sql

class Create(object):
    _class = None
    _cluster = None
    _type = None
    _from = None
    _to = None
    data = {}

    def __init__(self, type):
        super(Create, self).__init__()
        self._type = type
    
    def class_(self, _class):
        self._class = _class
        return self
        
    def cluster(self, cluster):
        self._cluster = cluster
        return self
    
    def from_(self, From):
        if self._type.lower() != 'edge':
            raise ValueError('Cannot set From/To to non-edge objects')
        self._from = From
        return self
    
    def to(self, to):
        if self._type.lower() != 'edge':
            raise ValueError('Cannot set From/To to non-edge objects')
        self._to = to
        return self

    def set(self, field, value = None):
        if value is None and isinstance(field, dict):
            self.content(field)
        if field and value:
            self.data[field] = value
        return self

    def content(self, obj):
        self.data.update(obj)
        return self

    def result(self, *args, **kwargs):
        prettify = kwargs.get('pretty', False)

        sql = 'CREATE %s %s' % (self._type, self._class)
        
        if prettify:
            sql += '\n'
        else:
            sql += ' '

        if self._type.lower() == 'edge':
            sql += " FROM %s TO %s " % (self._from, self._to)
        
        if self._cluster:
            sql += 'CLUSTER %s' % self._cluster
            if prettify:
                sql += '\n'
            else:
                sql += ' '
        
        if self.data:
            sql += 'CONTENT ' + json.dumps(self.data)
        print (sql)
        return sql

class Update(object):
    _class = None
    _cluster = None
    data = {}
    where_criteria = grouping.ConditionalGrouping()
    def __init__(self, _class):
        super(Update, self).__init__()
        self._class = _class

    def set(self, field, value = None):
        if value is None and isinstance(field, dict):
            self.content(field)
        if field and value:
            self.data[field] = value
        return self

    def content(self, obj):
        self.data.update(obj)
        return self

    def where(self, field, value = None, operator = None):
        conjunction = None
        if value is None and isinstance(field, dict):
            for f,v in field.items():
                if len(self.where_criteria) > 0:
                    conjunction = 'AND'
                self.where_criteria.append(expressions.ConditionExpression(f, v, operator=operator, conjunction=conjunction))
                
        else:
            if len(self.where_criteria) > 0:
                    conjunction = 'AND'
            self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def where_or(self, field, value, operator = None):
        conjunction = None
        if len(self.where_criteria) > 0:
            conjunction = 'OR'
        self.where_criteria.append(expressions.ConditionExpression(field, value, operator=operator, conjunction=conjunction))
        return self

    def result(self, *args, **kwargs):
        prettify = kwargs.get('pretty', False)

        sql = 'UPDATE %s' % self._class
        
        if prettify:
            sql += '\n'
        else:
            sql += ' '
        
        if self.data:
            sql += 'MERGE ' + json.dumps(self.data)
            if prettify:
                sql += '\n'
            else:
                sql += ' '

        if len(self.where_criteria) > 0:
            sql +=  'WHERE '
            sql +=  self.where_criteria.result()
            if prettify:
                sql += '\n'
            else:
                sql += ' '
        
        print (sql)
        return sql
