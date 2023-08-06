import unittest

from csl_data.item import CslDataItem
from csl_data._fragments import Date


class DateTest(unittest.TestCase):

    cls = CslDataItem

    _item_base_data = {
        'id': 'foo',
        'type': 'article',
    }

    def test_date_parts(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {}
        self.assertIsInstance(item['accessed'], Date)
        self.assertIsInstance(item.accessed, Date)
        accessed_date = item['accessed']
        accessed_date.date_parts is None
        accessed_date.date_parts = [[2004, 1, 21]]
        assert accessed_date.date_parts == [[2004, 1, 21]]
        accessed_date.date_parts = [[2004, 1, 21], [2004, 1, 22]]
        assert accessed_date.date_parts == [[2004, 1, 21], [2004, 1, 22]]

    def test_year(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {}
        accessed_date = item['accessed']
        self.assertRaises(KeyError, getattr, accessed_date, 'year')
        accessed_date.date_parts = [[2004, 1, 21]]
        assert accessed_date.year == 2004
        accessed_date.date_parts = [[2004, 1, 21], [2004, 1, 22]]
        assert accessed_date.year == 2004

    def test_year_setter(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {}
        accessed_date = item['accessed']
        self.assertRaises(KeyError, getattr, accessed_date, 'year')
        accessed_date.year = 2004
        assert accessed_date.year == 2004
        accessed_date.date_parts = [[2004], [2004]]
        assert accessed_date.year == 2004
        assert accessed_date._is_simple_year
        accessed_date.year = 2005
        assert accessed_date.year == 2005

    def test_year_setter_granularity(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {}
        accessed_date = item['accessed']
        accessed_date.date_parts = [[2004, 1, 1]]
        assert not accessed_date._is_simple_year
        self.assertRaises(AssertionError, setattr, accessed_date, 'year', 2005)

    def test_year_range(self):
        item = self.cls(self._item_base_data)
        item['accessed'] = {}
        accessed_date = item['accessed']
        accessed_date.date_parts = [[2004, 1, 21]]
        assert not accessed_date.is_range
        accessed_date.date_parts = [[2004, 1, 21], [2004, 1, 22]]
        assert accessed_date.is_range
        accessed_date.date_parts = [[2004, 1, 21], [2005, 1, 22]]
        assert accessed_date.is_range
        self.assertRaises(AssertionError, getattr, accessed_date, 'year')
