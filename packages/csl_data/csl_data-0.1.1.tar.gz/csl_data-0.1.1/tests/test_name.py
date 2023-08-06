import sys
import unittest

from csl_data.schema import _NAME_SCHEMA, _LOOSE_NAME_SCHEMA
from csl_data.item import CslDataItem, LooseCslDataItem
from csl_data._fragments import Name

from tests.utils import expected_failure_if

PY2 = sys.version_info[0] == 2


class NameTest(unittest.TestCase):

    cls = CslDataItem

    _item_base_data = {
        'id': 'foo',
        'type': 'article',
    }

    def test_name_author(self):
        item = self.cls(self._item_base_data)
        item['author'] = [{}]
        author_0 = item.author[0]
        assert author_0 is item.author[0]
        self.assertIsInstance(author_0, Name)
        assert not author_0.schema.additionalProperties
        assert author_0.schema._schema['properties'] == _NAME_SCHEMA['properties']
        author_0.family = 'Ray'
        assert 'family' in author_0
        assert author_0.family == 'Ray'
        assert author_0['family'].value == 'Ray'
        author_0.given = 'Oakley'
        assert author_0.given == 'Oakley'
        assert 'given' in author_0
        assert author_0['given'].value == 'Oakley'
        assert author_0.value == {'family': 'Ray', 'given': 'Oakley'}

    @expected_failure_if(PY2)
    def test_del(self):
        item = self.cls(self._item_base_data)
        item['author'] = [{}]
        author_0 = item.author[0]
        author_0.given = 'Oakley'
        author_0.family = 'Ray'
        del author_0.family
        assert author_0.value == {'given': 'Oakley'}

    def test_affiliation(self):
        item = LooseCslDataItem(self._item_base_data)
        item['author'] = [{}]
        author_0 = item.author[0]
        self.assertIsInstance(author_0, Name)
        assert author_0.schema.additionalProperties
        assert author_0.schema._schema['properties'] == _LOOSE_NAME_SCHEMA['properties']
        author_0.family = 'Ray'
        assert author_0.family == 'Ray'
        author_0.given = 'Oakley'
        assert author_0.given == 'Oakley'
        author_0.affiliation = 'Foo'
        assert author_0.affiliation == 'Foo'
        assert author_0.value == {
            'family': 'Ray', 'given': 'Oakley', 'affiliation': 'Foo'}
