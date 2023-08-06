"""Automatic JSON to Python bridge."""

from json_document.document import DocumentFragment


_SIMPLE_JSON_TYPES = ('string', 'number', 'boolean')


class AutoBridgedDocumentFragment(DocumentFragment):

    @staticmethod
    def _is_simple_type(name, schema):
        if schema.type in _SIMPLE_JSON_TYPES:
            return True
        if isinstance(schema.type, list):
            return all(x in _SIMPLE_JSON_TYPES for x in schema.type)
        return False

    @staticmethod
    def _rewrite_name(name):
        # There is one key that includes a `_`
        if name == 'archive_location':
            return name
        elif '_' in name:
            return name.replace('_', '-')
        else:
            return name

    def __getattr__(self, name):
        if name.startswith('__'):
            return object.__getattribute__(self, name)

        if name in dir(self):
            return object.__getattribute__(self, name)

        name = self._rewrite_name(name)

        if name in self:
            value = self[name]
            assert isinstance(value, DocumentFragment)
            if self._is_simple_type(name, value.schema):
                return value.value
            else:
                return value

        return None

    def __setattr__(self, name, new_value):
        if name in dir(self):
            super(AutoBridgedDocumentFragment, self).__setattr__(name, new_value)
            return

        name = self._rewrite_name(name)

        self[name] = new_value

    def __delattr__(self, name):
        if name in dir(self):
            super(AutoBridgedDocumentFragment, self).__delattr__[name]

        name = self._rewrite_name(name)

        del self[name]
