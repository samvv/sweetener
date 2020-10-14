
HORIZONTAL = 1
VERTICAL   = 2

def is_empty(iterator):
    try:
        next(iterator)
        return True
    except StopIteration:
        return False

def first(iterator):
    try:
        return next(iterator)
    except StopIteration:
        pass

def last(iterator):
    try:
        last_element = next(iterator)
    except StopIteration:
        return
    for element in iterator:
        last_element = element
    return last_element

from functools import reduce, wraps

def flatten(l):
    return sum(l, [])

foldl = reduce

def flip(func):
    @wraps(func)
    def newfunc(x, y):
        return func(y, x)
    return newfunc

def foldr(func, xs, acc):
    return reduce(flip(func), reversed(xs), acc)

def memoise(proc):
    def wrapped(self, *args, **kwargs):
        if not hasattr(self, '__memoised__'):
            self.__memoised__ = dict()
        mapping = self.__memoised__[proc.__name__]
        key = (tuple(args), tuple(kwargs.items()))
        if key in mapping:
            return key
        result = mapping[key] = proc(self, *args, **kwargs)
        return result
    return wrapped

def once(name):
    @property
    def get(self):
        if not hasattr(self, '__memoised__'):
            self.__memoised__ = dict()
        if name in self.__memoised__:
            return self.__memoised__[name]
        method = getattr(self, name)
        result = self.__memoised__[name] = method()
        return result
    return get

def has_method(value, name):
    return hasattr(value, name) \
        and callable(getattr(value, name))

def is_primitive(value):
    return value is None \
        or isinstance(value, str) \
        or isinstance(value, bool) \
        or isinstance(value, float) \
        or isinstance(value, int)

def pretty_enum(elements):
    try:
        element = next(elements)
    except StopIteration:
        raise ValueError(f'not enough elements provided')
    result = str(element)
    prev_element = None
    for element in elements:
        result += ', ' + prev_element
        prev_element = element
    if prev_element is None:
        return result
    return result + ' or ' + prev_element

def swap(a, i, j):
  a[i], a[j] = a[j], a[i]

def isheap(a, *, cmp=lambda a,b: a < b):
  n = 0
  m = 0
  while True:
    for i in [0, 1]:
      m += 1
      if m >= len(a):
        return True
      if cmp(a[n], a[m]):
        return False
    n += 1

def _sift_down(a, n, max, cmp):
  while True:
    biggest = n
    c1 = 2*n + 1
    c2 = c1 + 1
    for c in [c1, c2]:
        if c < max and cmp(a[biggest], a[c]):
            biggest = c
    if biggest == n:
      return
    swap(a, n, biggest)
    n = biggest

def heapify(a, *, cmp=lambda a, b: a < b):
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

def get(value, path):
    if isinstance(path, str):
        path = path.split('.')
    if not isinstance(path, list):
        path = [path]
    for chunk in path:
        if isinstance(value, tuple) or isinstance(value, list):
            value = value[int(chunk)]
        elif isinstance(value, object):
            value = getattr(value, chunk)
        elif isinstance(value, dict):
            value = value[chunk]
        else:
            raise NotImplementedError(f"did not know how to get {chunk} from {value}")
    return value

def lift(proc, key):
    def lifted(*args):
        return proc(*(get(arg, key) for arg in args))
    return lifted

def heapsort(a, cmp=lambda a, b: a < b, key=None):
    if key is not None:
        cmp = lift(cmp, key)
    heapify(a, cmp=cmp)
    sortheap(a, cmp=cmp)

def quicksort(arr, low=None, high=None, cmp=lambda a, b: a < b):

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

# def eq(v1, v2):
#     if (isinstance(v1, str) and isinstance(v2, str)) \
#             or (isinstance(v1, bool) and isinstance(v2, bool)) \
#             or (isinstance(v1, int) and isinstance(v2, int)) \
#             or (isinstance(v1, float) and isinstance(v2, float)):
#         return v1 == v2
#     elif (isinstance(v1, tuple) and isinstance(v2, tuple)) \
#             or (isinstance(v1, list) and isinstance(v2, list)):
#         if len(v1) != len(v2):
#             return False
#         for i in range(0, len(v1)):
#             if not eq(v1[i], v2[i]):
#                 return False
#         return True
#     else:
#         return False
