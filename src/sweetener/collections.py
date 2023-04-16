
from typing import TypeVar, Iterable, Generic

from .bidict import bidict

K = TypeVar('K')
V = TypeVar('V')

class MultiDict(Generic[K, V]):

    def __init__(self) -> None:
        super().__init__()
        self._mapping = dict()

    def get(self, key: K, default=[]):
        if key not in self._mapping or not self._mapping[key]:
            return default
        return self._mapping[key]

    def add(self, key: K, value: V) -> None:
        if key not in self._mapping:
            self._mapping[key] = []
        self._mapping[key].append(value)

    def update(self, other: 'MultiDict[K, V]'):
        for k, v in other.items():
            self.add(k, v)

    def __getitem__(self, key: K) -> Iterable[V]:
        return self._mapping[key]

    def items(self):
        for k, l in self._mapping.items():
            for v in l:
                yield k, v

