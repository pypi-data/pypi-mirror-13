class AliasExpression(object):
    """AliasExpression DOCS"""
    @property
    def field_name(self):
        """I am the 'field_name' property."""
        return self._field_name
    @field_name.setter
    def field_name(self, value):
        self._field_name = value
    @field_name.deleter
    def field_name(self):
        del self._field_name

    @property
    def alias(self):
        """I am the 'alias' property."""
        return self._alias
    @alias.setter
    def alias(self, value):
        self._alias = value
    @alias.deleter
    def alias(self):
        del self._alias

    def __init__(self, field_name, alias=None, *args, **kwargs):
        super(self.__class__, self).__init__()
        if isinstance(field_name, list):
            self.field_name, self.alias = field_name
        elif " as " in field_name.lower():
            self.field_name, self.alias = field_name.split(' as ')
        else:
            self.field_name = field_name
            self.alias = alias

    def result(self):
        field = str(self.field_name) \
            .replace("\\", '') \
            .replace('"', '') \
            .replace("'", '')

        if self.alias:
            alias = str(self.alias) \
                .replace("\\", '') \
                .replace('"', '') \
                .replace("'", '')
            return "%s AS %s" % (field, alias)
        else:
            return field

class ConditionExpression(object):
    @property
    def field(self):
        """I am the 'field' property."""
        return self._field
    @field.setter
    def field(self, value):
        self._field = value
    @field.deleter
    def field(self):
        del self._field

    @property
    def value(self):
        """I am the 'value' property."""
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
    @value.deleter
    def value(self):
        del self._value
    @property
    def operator(self):
        """I am the 'operator' property."""
        return self._operator
    @operator.setter
    def operator(self, operator):
        self._operator = operator
    @operator.deleter
    def operator(self):
        del self._value

    def __init__(self, field, value, *args, **kwargs):
        self.field = field
        self.value = value
        self.operator = '=' if kwargs.get('operator') is None else kwargs['operator']
        self.conjunction = kwargs.get('conjunction')

    def result(self):
        field = str(self.field) \
            .replace("\\", "") \
            .replace('"', '') \
            .replace("'", "")

        try:
            value = float(self.value)
        except ValueError:
            value = str(self.value) \
                .replace("\\", r"\\") \
                .replace('"', r'\"') \
                .replace("'", r"\'")

            value = "'%s'" % value
        
        res = "%s %s %s" % (field, self.operator, value)

        if self.conjunction:
            res = "%s %s" % (self.conjunction, res)
        
        return res

class OrderByExpression(object):
    def __init__(self, field, orientation = 'ASC'):
        super(OrderByExpression, self).__init__()

        if isinstance(field, list):
            self.field, self.orientation = field[0:2]
        elif 'ASC' in field.upper() or 'DESC' in field.upper():
            self.field, self.orientation = field.split(' ')
        else:
            self.field = field
            self.orientation = orientation
    def result(self):
        return "%s %s" % (self.field, self.orientation)