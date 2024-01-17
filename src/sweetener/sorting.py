
from abc import abstractmethod
from typing import Any, Callable, List, Optional, Protocol, TypeVar

from .common import swap, lift

K = TypeVar('K')

class Comparable(Protocol):
    def __lt__(self, value: Any, /) -> bool: ...

foo: Comparable = int(1)

T = TypeVar('T', bound=Comparable)

CompareFn = Callable[[T, T], bool]

def _default_cmp(a: T, b: T) -> bool:
    return a < b

def isheap(arr: List[T], cmp: Optional[CompareFn] = None):
    if cmp is None:
        cmp = _default_cmp
    n = len(arr)
    for i in range(0, n // 2):
        if cmp(arr[i], arr[2 * i]):
            return False
        if cmp(arr[i], arr[2 * i + 1]):
            return False
    if n % 2 != 0 and cmp(arr[n // 2], arr[n-1]):
        return False
    return True

def _sift_down(arr: List[T], n: int, max: int, cmp: CompareFn) -> None:
  while True:
    biggest = n
    c1 = 2*n
    c2 = c1 + 1
    if c1 < max and cmp(arr[biggest], arr[c1]):
        biggest = c1
    if c2 < max and cmp(arr[biggest], arr[c2]):
        biggest = c2
    if biggest == n:
      return
    swap(arr, n, biggest)
    n = biggest

def heapify(arr: List[T], *, cmp: Optional[CompareFn] = None) -> None:
    if cmp is None:
        cmp = _default_cmp
    i = len(arr) // 2
    max = len(arr)
    while i >= 0:
      _sift_down(arr, i, max, cmp)
      i -= 1

def heapinsert(arr: List[T], v: T, *, cmp: Optional[CompareFn] =None, key=None) -> None:
    if cmp is None:
        cmp = _default_cmp
    if key is not None:
        cmp = lift(cmp, key)
    arr.append(v)
    _sift_down(arr, 0, len(arr)-1, cmp)

def sortheap(a: List[T], *, cmp: Optional[CompareFn] = None, key=None) -> None:
    if cmp is None:
        cmp = _default_cmp
    if key is not None:
        cmp = lift(cmp, key)
    j = len(a) - 1
    while j > 0:
        swap(a, 0, j)
        _sift_down(a, 0, j, cmp)
        j -= 1

def heapsort(a: List[T], *, cmp: Optional[CompareFn] = None, key=None) -> None:
    if cmp is None:
        cmp = _default_cmp
    if key is not None:
        cmp = lift(cmp, key)
    heapify(a, cmp=cmp)
    sortheap(a, cmp=cmp)

def quicksort(arr: List[T], low: Optional[int] = None, high: Optional[int] = None, cmp: Optional[CompareFn] = None):

    if cmp is None:
        cmp = _default_cmp
    if low is None:
        low = 0
    if high is None:
        high = len(arr)-1

    def partition(low, high):
        i = low-1
        pivot = arr[high]
        for j in range(low, high):
            if cmp(arr[j], pivot):
                i = i+1
                swap(arr, i, j)
        swap(arr, i+1, high)
        return i+1

    if low < high:
        pi = partition(low,high)
        quicksort(arr, low, pi-1, cmp=cmp)
        quicksort(arr, pi+1, high, cmp=cmp)

