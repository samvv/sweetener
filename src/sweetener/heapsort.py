
from typing import Callable, Protocol, TypeVar

from .common import swap, lift

class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool:
        raise NotImplementedError

T = TypeVar('T', bound=Comparable)

CompareFn = Callable[[T, T], bool]

def isheap(a: list[T], *, cmp: CompareFn = lambda a,b: a < b):
    n = len(a)
    for i in range(0, n // 2):
        if cmp(a[i], a[2 * i]):
            return False
        if cmp(a[i], a[2 * i + 1]):
            return False
    if n % 2 != 0 and cmp(a[n // 2], a[n-1]):
        return False
    return True

def _sift_down(a: list[T], n: int, max: int, cmp: CompareFn):
  while True:
    biggest = n
    c1 = 2 * n
    c2 = c1 + 1
    if c1 < max and cmp(a[biggest], a[c1]):
        biggest = c1
    if c2 < max and cmp(a[biggest], a[c2]):
        biggest = c2
    if biggest == n:
      return
    swap(a, n, biggest)
    n = biggest

def heapify(a: list[T], cmp: CompareFn= lambda a, b: a < b):
    i = len(a) // 2
    max = len(a)
    while i >= 0:
      _sift_down(a, i, max, cmp)
      i -= 1

def heapinsert(a, v, *, cmp=lambda a, b: a < b, key=None):
    if key is not None:
        cmp = lift(cmp, key)
    a.append(v)
    _sift_down(a, 0, len(a)-1, cmp)

def sortheap(a, *, cmp=lambda a, b: a < b, key=None):
    if key is not None:
        cmp = lift(cmp, key)
    j = len(a) - 1
    while j > 0:
        swap(a, 0, j)
        _sift_down(a, 0, j, cmp)
        j -= 1

def heapsort(a: list[T], cmp: CompareFn=lambda a, b: a < b, key=None):
    if key is not None:
        cmp = lift(cmp, key)
    heapify(a, cmp=cmp)
    sortheap(a, cmp=cmp)

