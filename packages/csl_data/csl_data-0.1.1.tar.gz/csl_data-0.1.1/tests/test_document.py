import unittest

from csl_data._fragments import Item
from csl_data.document import CslDataDocument


class DocumentTest(unittest.TestCase):

    cls = CslDataDocument

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
    def test_validate(self):
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
