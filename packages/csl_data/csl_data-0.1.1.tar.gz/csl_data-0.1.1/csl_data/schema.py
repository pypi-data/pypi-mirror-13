import os.path

import json

from json_document.document import Document

from csl_data._fragments import Date, Item, Name

_GITHUB_RAW = 'https://raw.githubusercontent.com/'
SCHEMA_URL = _GITHUB_RAW + 'citation-style-language/schema/master/csl-data.json'

SCHEMA_JSON_FILENAME = os.path.join(os.path.split(__file__)[0], 'csl-data.json')

SCHEMA = json.loads(open(SCHEMA_JSON_FILENAME, 'r').read())

ITEM_SCHEMA = SCHEMA['items']
ITEM_SCHEMA['__fragment_cls'] = Item

ITEM_TYPES = ITEM_SCHEMA['properties']['type']['enum']

_DATE_SCHEMA = ITEM_SCHEMA['properties']['accessed']['type'][0]
_NAME_SCHEMA = ITEM_SCHEMA['properties']['author']['items']['type'][0]
_DATE_SCHEMA['additionalProperties'] = False
_NAME_SCHEMA['additionalProperties'] = False
_DATE_SCHEMA['__fragment_cls'] = Date
_NAME_SCHEMA['__fragment_cls'] = Name

assert 'id' in ITEM_SCHEMA['properties']['accessed']
assert 'id' in ITEM_SCHEMA['properties']['author']['items']

ITEM_SCHEMA['properties']['accessed']['type'] = _DATE_SCHEMA
ITEM_SCHEMA['properties']['accessed']['__fragment_cls'] = Date
ITEM_SCHEMA['properties']['author']['items']['type'] = _NAME_SCHEMA
ITEM_SCHEMA['properties']['author']['items']['__fragment_cls'] = Name

LOOSE_SCHEMA = SCHEMA.copy()

LOOSE_ITEM_SCHEMA = ITEM_SCHEMA.copy()
LOOSE_ITEM_SCHEMA['additionalProperties'] = {'type': 'string'}
LOOSE_ITEM_SCHEMA['properties'] = ITEM_SCHEMA['properties'].copy()

LOOSE_SCHEMA['items'] = LOOSE_ITEM_SCHEMA


_LOOSE_DATE_SCHEMA = _DATE_SCHEMA.copy()
_LOOSE_NAME_SCHEMA = _NAME_SCHEMA.copy()

_LOOSE_DATE_SCHEMA['additionalProperties'] = {'type': 'string'}
_LOOSE_NAME_SCHEMA['additionalProperties'] = {'type': 'string'}

LOOSE_ITEM_SCHEMA['properties']['accessed'] = ITEM_SCHEMA['properties']['accessed'].copy()
LOOSE_ITEM_SCHEMA['properties']['accessed']['type'] = _LOOSE_DATE_SCHEMA

LOOSE_ITEM_SCHEMA['properties']['author'] = ITEM_SCHEMA['properties']['author'].copy()
LOOSE_ITEM_SCHEMA['properties']['author']['items'] = (
    ITEM_SCHEMA['properties']['author']['items'].copy())
LOOSE_ITEM_SCHEMA['properties']['author']['items']['type'] = _LOOSE_NAME_SCHEMA


def _fix_refs(schema, loose=False):
    if loose is False:
        _date_schema = _DATE_SCHEMA
        _name_schema = _NAME_SCHEMA
    else:
        _date_schema = _LOOSE_DATE_SCHEMA
        _name_schema = _LOOSE_NAME_SCHEMA

    assert 'properties' in _date_schema
    assert 'properties' in _name_schema

    for key, value in schema['items']['properties'].items():
        assert isinstance(value, dict)

        if value.get('type') == 'array':
            value = value['items']

        if key == 'author':
            value.update(_name_schema)
            assert 'properties' in value
            continue
        elif key == 'accessed':
            value.update(_date_schema)
            assert 'properties' in value
            continue

        if '$ref' not in value:
            continue

        if value['$ref'] == 'name-variable':
            value.update(_name_schema)
            assert 'properties' in value
        elif value['$ref'] == 'date-variable':
            value.update(_date_schema)
            assert 'properties' in value


_fix_refs(SCHEMA, loose=False)
_fix_refs(LOOSE_SCHEMA, loose=True)


class _CslDataSchema(Document):

    document_schema = SCHEMA
    _loose = False

    def __init__(self, value=None):
        """Constructor."""
        # Re-do initialisation here to see debugging during py.test
        # _fix_refs(self.document_schema, loose=self._loose, debug=True)

        if value is None:
            if self.document_schema['type'] == 'array':
                value = []
            else:
                value = {}

        super(_CslDataSchema, self).__init__(value)

    @property
    def _additional_properties(self):
        return [key for key in self.value.keys()
                if key not in self.schema.properties]

    @property
    def _unknown_metadata(self):
        data = dict((key, value) for (key, value) in self.value.items()
                    if key in self._additional_properties)
        return data


class _LooseCslDataSchema(_CslDataSchema):

    document_schema = LOOSE_SCHEMA
    _loose = True
