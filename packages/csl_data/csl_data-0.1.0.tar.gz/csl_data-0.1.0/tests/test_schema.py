import unittest

from csl_data.schema import _CslDataSchema, _LooseCslDataSchema
from csl_data.schema import (
    SCHEMA,
    ITEM_SCHEMA,
    _DATE_SCHEMA,
    _NAME_SCHEMA,
    LOOSE_SCHEMA,
    LOOSE_ITEM_SCHEMA,
    _LOOSE_DATE_SCHEMA,
    _LOOSE_NAME_SCHEMA,
)
from csl_data._fragments import Date, Item, Name


class SchemaTestBase(object):

    cls = _CslDataSchema

    _item_base_data = {
        'id': 'foo',
        'type': 'article',
    }

    def test_list_create(self):
        d = self.cls()
        d.value.append(self._item_base_data)
        assert d[0]
        assert d[0].schema

    @unittest.expectedFailure
    def test_list_validate(self):
        d = self.cls()
        d.value.append(self._item_base_data)
        d.validate()

    def test_item(self):
        d = self.cls()
        d.value.append(self._item_base_data)
        assert isinstance(d[0], Item)
        item = d[0]
        assert item.value == self._item_base_data
        assert item['id'].value == 'foo'
        assert item['type'].value == 'article'

    def test_item_unknown_property_undefined(self):
        item_dict = self._item_base_data.copy()
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        self.assertRaises((AttributeError, KeyError), item.__getitem__, 'foo')

    def test_name_property(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley'}]
        d = self.cls()
        d.value.append(item_dict)
        item = d[0]
        author_0 = item['author'][0]
        assert isinstance(author_0, Name)
        assert author_0.value == item_dict['author'][0]
        assert author_0.schema
        assert author_0.schema._schema
        assert isinstance(author_0.schema.type, dict)
        assert 'properties' in _NAME_SCHEMA
        assert 'properties' in author_0.schema._schema['type']
        assert 'properties' in author_0.schema._schema
        assert len(author_0.schema.properties)
        assert author_0.family == 'Ray'
        assert author_0.given == 'Oakley'

    def test_name_property_ref(self):
        item = self._item_base_data.copy()
        item['composer'] = [{'family': 'Ray', 'given': 'Oakley'}]
        d = self.cls()
        d.value.append(item)
        item = d[0]
        composer_0 = item['composer'][0]
        assert isinstance(composer_0, Name)
        assert len(composer_0.schema.properties)
        assert composer_0.family == 'Ray'
        assert composer_0.given == 'Oakley'

    def test_name_unknown_property_undefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley'}]
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        name_0 = item['author'][0]
        self.assertRaises((AttributeError, KeyError), name_0.__getitem__, 'foo')

    def test_date_property(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]]}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        item['accessed'] = {'date-parts': [[2004, 1, 21]], 'literal': 'foo'}
        accessed_date = item['accessed']
        assert accessed_date.value == item_dict['accessed']
        assert isinstance(accessed_date, Date)
        assert accessed_date.schema
        assert accessed_date.schema._schema
        assert isinstance(accessed_date.schema.type, dict)
        assert 'properties' in accessed_date.schema._schema['type']
        assert 'properties' in accessed_date.schema._schema
        assert len(accessed_date.schema.properties)
        accessed_date['date-parts'].value = [[2004, 1, 21]]
        assert accessed_date['date-parts'].value == [[2004, 1, 21]]
        assert accessed_date['literal'].value == 'foo'
        assert accessed_date.literal == 'foo'

    def test_date_property_ref(self):
        item_dict = self._item_base_data.copy()
        item_dict['issued'] = {'date-parts': [[2004, 1, 21]]}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['issued']
        assert date.value == item_dict['issued']
        assert isinstance(date, Date)

    def test_date_unknown_property_undefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]]}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['accessed']
        assert date.value == item_dict['accessed']
        assert isinstance(date, Date)
        assert 'foo' not in date
        self.assertRaises((AttributeError, KeyError), date.__getitem__, 'foo')


class TestStrictSchema(SchemaTestBase, unittest.TestCase):

    def test_strict(self):
        assert SCHEMA is not LOOSE_SCHEMA
        assert SCHEMA != LOOSE_SCHEMA
        assert _CslDataSchema.document_schema is not _LooseCslDataSchema.document_schema
        assert ITEM_SCHEMA is not LOOSE_ITEM_SCHEMA
        assert ITEM_SCHEMA != LOOSE_ITEM_SCHEMA
        assert ITEM_SCHEMA['additionalProperties'] is False
        assert _DATE_SCHEMA['additionalProperties'] is False
        assert _NAME_SCHEMA['additionalProperties'] is False

        schema = self.cls.document_schema
        assert schema == SCHEMA
        assert schema['items']['additionalProperties'] is False
        assert schema['items']['properties']['accessed']['type']['additionalProperties'] is False
        assert schema['items']['properties']['author']['items']['type']['additionalProperties'] is False
        assert _DATE_SCHEMA == schema['items']['properties']['accessed']['type']
        assert _NAME_SCHEMA == schema['items']['properties']['author']['items']['type']

    def test_item_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['foo'] = 'bar'
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        assert item.schema.additionalProperties is False
        assert 'foo' in item
        self.assertRaises(AttributeError, item.__getitem__, 'foo')
        self.assertRaises(AttributeError, item.__setitem__, 'foo', 'bar')

    def test_item_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        assert 'foo' not in item
        self.assertRaises(AttributeError, item.__setitem__, 'foo', 'bar')

    def test_name_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley', 'foo': 'bar'}]
        d = self.cls()
        d.value.append(item_dict)
        item = d[0]
        assert isinstance(item['author'][0], Name)
        name_0 = item['author'][0]
        assert name_0.schema.additionalProperties is False
        assert 'foo' in name_0
        self.assertRaises(AttributeError, name_0.__getitem__, 'foo')
        self.assertRaises(AttributeError, name_0.__setitem__, 'foo', 'bar')

    def test_name_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley'}]
        d = self.cls()
        d.value.append(item_dict)
        item = d[0]
        assert isinstance(item['author'][0], Name)
        name_0 = item['author'][0]
        self.assertRaises(AttributeError, name_0.__getitem__, 'foo')
        self.assertRaises(AttributeError, name_0.__setitem__, 'foo', 'bar')

    def test_date_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]], 'foo': 'bar'}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['accessed']
        assert isinstance(date, Date)
        assert date.schema.additionalProperties is False
        assert date.value == item_dict['accessed']
        assert 'foo' in date
        self.assertRaises(AttributeError, date.__getitem__, 'foo')
        self.assertRaises(AttributeError, date.__setitem__, 'foo', 'bar')

    def test_date_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]]}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['accessed']
        assert date.schema.additionalProperties is False
        assert date.value == item_dict['accessed']
        assert isinstance(date, Date)
        assert 'foo' not in date
        self.assertRaises(AttributeError, date.__getitem__, 'foo')
        self.assertRaises(AttributeError, date.__setitem__, 'foo', 'bar')


class TestLooseSchema(SchemaTestBase, unittest.TestCase):

    cls = _LooseCslDataSchema

    def test_loose(self):
        schema = self.cls.document_schema
        assert schema == LOOSE_SCHEMA
        assert schema['items']['additionalProperties'] is not False

        assert _LOOSE_DATE_SCHEMA['additionalProperties'] is not False
        assert _LOOSE_NAME_SCHEMA['additionalProperties'] is not False

        assert schema['items']['properties']['accessed']['type']['additionalProperties'] is not False
        assert schema['items']['properties']['author']['items']['type']['additionalProperties'] is not False

    def test_item_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['foo'] = 'bar'
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        assert 'foo' in item
        assert item['foo'].value == 'bar'

    def test_item_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        item['foo'] = 'bar'
        assert 'foo' in item
        assert item['foo'].value == 'bar'

    def test_name_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley', 'foo': 'bar'}]
        d = self.cls()
        d.value.append(item_dict)
        item = d[0]
        assert isinstance(item['author'][0], Name)
        name_0 = item['author'][0]
        assert 'foo' in name_0
        assert name_0['foo'].value == 'bar'

    def test_name_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        item_dict['author'] = [{'family': 'Ray', 'given': 'Oakley'}]
        d = self.cls()
        d.value.append(item_dict)
        item = d[0]
        assert isinstance(item['author'][0], Name)
        name_0 = item['author'][0]
        name_0['foo'] = 'bar'
        assert 'foo' in name_0
        assert name_0['foo'].value == 'bar'

    def test_date_unknown_property_predefined(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]], 'foo': 'bar'}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['accessed']
        assert date.value == item_dict['accessed']
        assert isinstance(date, Date)
        assert 'foo' in date
        assert date['foo'].value == 'bar'

    def test_date_unknown_property_defined(self):
        item_dict = self._item_base_data.copy()
        item_dict['accessed'] = {'date-parts': [[2004, 1, 21]]}
        d = self.cls()
        d.value.append(item_dict)
        assert isinstance(d[0], Item)
        item = d[0]
        date = item['accessed']
        assert date.value == item_dict['accessed']
        assert isinstance(date, Date)
        assert 'foo' not in date
        date['foo'] = 'bar'
        assert 'foo' in date
        assert date['foo'].value == 'bar'
