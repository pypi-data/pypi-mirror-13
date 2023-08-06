import logging

from .util import read_row

logger = logging.getLogger(__name__)


class Row:

    def __init__(self, values, headers=None):
        self.__dict__['_values'] = values
        self.__dict__['_headers'] = headers

    def __iter__(self):
        for value in self.__dict__['_values']:
            yield value

    def keys(self):
        return list(self.__dict__['_headers'])

    def values(self):
        return self.__dict__['_values']

    def items(self):
        if self.__dict__['_headers']:
            return ((h, v) for h, v in
                    zip(self.__dict__['_headers'], self.__dict__['_values']))
        else:
            return ((i, v) for i, v in enumerate(self.__dict__['_values']))

    def __getstate__(self):
        return self.__dict__['_values'], self.__dict__['_headers']

    def __setstate__(self, state):
        self.__dict__['_values'], self.__dict__['_headers'] = state

    def __getitem__(self, key_or_index):
        index = self._internal_index(key_or_index)

        return self.__dict__['_values'][index]

    def __setitem__(self, key_or_index):
        raise TypeError("item assignment not supported")

    def __getattr__(self, key):
        index = self._internal_index(key)

        return self.__dict__['_values'][index]

    def __setattr__(self, key, value):
        raise TypeError("item assignment not supported")

    def _internal_index(self, key_or_index):
        if type(key_or_index) == int:
            index = key_or_index
        else:
            if key_or_index not in self.__dict__['_headers']:
                raise KeyError(key_or_index)
            else:
                index = self.__dict__['_headers'][key_or_index]

        return index

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            for p1, p2 in zip(self.iteritems(), other.iteritems()):
                if p1 != p2:
                    return False

            return True
        except AttributeError:
            return False


class RowGenerator:

    def __init__(self, headers, types=None, none_string="NULL"):
        if headers is not None:
            headers = dict((h, i) for i, h in enumerate(headers))
            if types is not None:
                assert len(types) == len(headers), \
                    "Length of types {0} must match headers {1}" \
                    .format(len(types), headers)

        self.headers = headers
        self.types = types
        self.none_string = none_string

    def __call__(self, line):
        values = list(read_row(line, types=self.types,
                               none_string=self.none_string))
        if self.headers and len(values) != len(self.headers):
            raise ValueError("Expected {0} values and got {1}."
                             .format(len(self.headers), len(values)))

        return Row(values, self.headers)
