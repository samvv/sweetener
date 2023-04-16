
class bidict:

    def __init__(self, elements=None):
        self._key_to_value = dict()
        self._value_to_key = dict()
        if elements is not None:
            for k, v in elements:
                self._key_to_value[k] = v
                self._value_to_key[v] = k

    def __iter__(self):
        return iter(self._key_to_value)

    def __getitem__(self, key):
        return self._key_to_value[key]

    def get_key(self, value):
        return self._value_to_key[value]

    def __setitem__(self, key, value):
        self._key_to_value[key] = value
        self._value_to_key[value] = key

