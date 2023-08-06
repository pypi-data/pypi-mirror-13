from csl_data._bridge import AutoBridgedDocumentFragment


class Date(AutoBridgedDocumentFragment):

    @staticmethod
    def _is_simple_type(name, schema):
        if name == 'date-parts':
            return True
        return AutoBridgedDocumentFragment._is_simple_type(name, schema)

    @property
    def start(self):
        if self.date_parts:
            return self.date_parts[0]
        else:
            raise KeyError('no date_parts')

    @property
    def end(self):
        if self.date_parts:
            return self.date_parts[1]
        else:
            raise KeyError('no date_parts')

    @property
    def is_range(self):
        return len(self.date_parts) > 1

    @property
    def _is_simple_year(self):
        # Ensure there is a sensible year member of the start dict
        self.year

        if len(self.start) > 1:
            return False

        if self.is_range and len(self.end) > 1:
            return False

        return True

    @property
    def year(self):
        """Year."""
        start_year = self.start[0]
        if self.is_range:
            assert start_year == self.end[0]
        return start_year

    @year.setter
    def year(self, value):
        if 'date-parts' in self:
            assert self._is_simple_year
        self.date_parts = [[value]]
