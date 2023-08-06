import json


class SchemaCollection(object):
    def __init__(self, data):
        if not isinstance(data, list):
            raise ValueError('A list is required to form SchemaCollection')

        self._items = []
        for item in data:
            schema = Schema().from_dict(item)
            self._items.append(schema)

        self._iter_pos = -1

    def __iter__(self):
        return self

    def next(self):
        self._iter_pos += 1
        if self._iter_pos >= len(self._items):
            raise StopIteration()
        else:
            return self._items[self._iter_pos]

    def __str__(self):
        return '\n'.join([str(item) for item in self._items])


class Schema(object):
    """
    A class that represents the schema (structure) of the data that is going to be sent
    to the Data-API backend.
    """

    FIELD_TYPE_INT = 'int'
    FIELD_TYPE_STRING = 'string'
    FIELD_TYPE_BOOL = 'boolean'
    FIELD_TYPE_DOUBLE = 'double'
    FIELD_TYPE_FLOAT = 'float'
    FIELD_TYPE_LONG = 'long'
    FIELD_TYPE_BYTES = 'bytes'

    def __init__(self, name=None, namespace=None, doc=None, fields=None):
        """
        Initialize the object with required data
        :param name: The required name of schema
        :param namespace: A string used to generate the java class (com.company.product)
        :param doc: A documentation string describing the schema
        :param fields: A list of dicts containing name and type of fields
        """
        self.id = None
        self.name = name
        self.namespace = namespace
        self.doc = doc
        self.type = 'record'
        self.fields = fields

        self.validate_fields()

    def validate_fields(self):
        """
        Make sure that the 'fields' array contains valid
        field definitions.
        :return: Whether the fields are valid or not
        :rtype: bool
        """
        if not self.fields:
            return True

        for field in self.fields:
            field_keys = field.keys()
            if 'name' not in field_keys or 'type' not in field_keys:
                raise ValueError(
                    'Fields %s should provide name, type subfields' % field)

        return True

    def from_dict(self, data):
        """
        Transform a dictionary into a Schema object
        :param data: a dict of schema values
        """
        if not isinstance(data, dict):
            raise ValueError('Data should be a dictionary')

        schema = json.loads(data['schema'])
        for key, value in schema.iteritems():
            if not hasattr(self, key):
                continue
            setattr(self, key, value)
        self.id = data['id']

        return self

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __unicode__(self):
        return self.__str__()
