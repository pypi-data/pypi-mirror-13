import unittest

from csl_data.item import CslDataItem, LooseCslDataItem
from csl_data._fragments import Date, Item, Name


class ItemTest(unittest.TestCase):

    cls = CslDataItem

    _item_base_data = {
        'id': 'foo',
        'type': 'article',
    }

    def test_empty_item(self):
        item = self.cls()
        self.assertIsInstance(item, Item)

    @unittest.expectedFailure
    def test_item_validate(self):
        item = self.cls(self._item_base_data)
        item.validate()

    def test_item_getitem(self):
        item = self.cls(self._item_base_data)
        assert item.value == self._item_base_data
        assert item['id'].value == 'foo'
        assert item['type'].value == 'article'

    def test_item_setitem(self):
        item = self.cls(self._item_base_data)
        assert item.value == self._item_base_data
        item['id'] = 'bar'
        assert item['id'].value == 'bar'

    def test_item_getattr(self):
        item = self.cls()
        assert item.id is None
        assert item.type is None
        item.value = self._item_base_data.copy()
        assert item.value == self._item_base_data
        assert item.id == 'foo'
        assert item.type == 'article'

    def test_item_unknown_property(self):
        item = self.cls(self._item_base_data)
        assert item.value == self._item_base_data
        self.assertRaises(AttributeError, item.__setitem__, 'foo', 'bar')

    def test_author(self):
        item = self.cls(self._item_base_data)
        item['author'] = []
        item.value['author'].append({'family': 'Ray', 'given': 'Oakley'})
        self.assertIsInstance(item.author[0], Name)
        item.author[0] = {'family': 'Ray', 'given': 'Oakley'}
        self.assertIsInstance(item.author[0], Name)

    @unittest.expectedFailure
    def test_author_list_auto(self):
        item = self.cls(self._item_base_data)
        # This fails here:
        assert item.author is not None
        assert item.author[0] is None
        item.author[0] = {'family': 'Ray', 'given': 'Oakley'}
        assert item.value == {'author': [{'family': 'Ray', 'given': 'Oakley'}]}

    @unittest.expectedFailure
    def test_author_list_equal(self):
        item = self.cls(self._item_base_data)
        item['author'] = []
        self.assertEqual(item.author, [])

    def test_composer(self):
        item = self.cls(self._item_base_data)
        item['composer'] = [{}]
        composer_0 = item.composer[0]
        self.assertIsInstance(composer_0, Name)
        composer_0.family = 'Ray'
        assert composer_0.family == 'Ray'
        composer_0.given = 'Oakley'
        assert composer_0.given == 'Oakley'

    def test_accessed(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {'date-parts': [[2004, 1, 21]], 'literal': 'foo'}
        self.assertIsInstance(item['accessed'], Date)
        self.assertIsInstance(item.accessed, Date)


class LooseItemTest(unittest.TestCase):

    cls = LooseCslDataItem

    _item_base_data = {
        'id': 'foo',
        'type': 'article',
    }

    def test_empty_item(self):
        item = self.cls()
        self.assertIsInstance(item, Item)

    @unittest.expectedFailure
    def test_item_validate(self):
        item = self.cls(self._item_base_data)
        item.validate()

    def test_item_unknown_property(self):
        item = self.cls(self._item_base_data)
        assert item.value == self._item_base_data
        item['foo'] = 'bar'
        assert item['foo'].value == 'bar'
