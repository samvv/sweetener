

from typing import Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar

_K = TypeVar('_K')
_V = TypeVar('_V')
_T = TypeVar('_T')

def omit(mapping: dict[_K, _V], *keys: List[_K]) -> dict[_K, _V]:
     result = dict()
     for k, v in mapping.items():
         if k not in keys:
             result[k] = v
     return result

class MultiDict(Generic[_K, _V]):

    def __init__(self) -> None:
        super().__init__()
        self._mapping = dict()

    def get(self, key: _K, default=[]):
        if key not in self._mapping or not self._mapping[key]:
            return default
        return self._mapping[key]

    def add(self, key: _K, value: _V) -> None:
        if key not in self._mapping:
            self._mapping[key] = []
        self._mapping[key].append(value)

    def update(self, other: 'MultiDict[_K, _V]'):
        for k, v in other.items():
            self.add(k, v)

    def __getitem__(self, key: _K) -> Iterable[_V]:
        return self._mapping[key]

    def items(self):
        for k, l in self._mapping.items():
            for v in l:
                yield k, v

class bidict(Generic[_K, _V]):

    def __init__(self, elements: Optional[Iterable[Tuple[_K, _V]]] = None):
        self._key_to_value = dict[_K, _V]()
        self._value_to_key = dict[_V, _K]()
        if elements is not None:
            for k, v in elements:
                self._key_to_value[k] = v
                self._value_to_key[v] = k

    def __iter__(self) -> Iterator[_K]:
        return iter(self._key_to_value)

    def __getitem__(self, key: _K) -> _V:
        return self._key_to_value[key]

    def get_key(self, value: _V, default: _K | _T = None) -> _K | _T:
        return self._value_to_key.get(value, default)

    def get(self, key: _K, default: _V | _T = None) -> _V | _T:
        return self._key_to_value.get(key, default)

    def keys(self) -> Iterable[_K]:
        return self._key_to_value.keys()

    def values(self) -> Iterable[_V]:
        return self._key_to_value.values()

    def __setitem__(self, key: _K, value: _V) -> None:
        self._key_to_value[key] = value
        self._value_to_key[value] = key

