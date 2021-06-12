
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

def pretty_enum(elements, default='nothing'):
    elements = iter(elements)
    try:
        element = next(elements)
    except StopIteration:
        return default
    result = str(element)
    try:
        prev_element = next(elements)
    except StopIteration:
        return result
    while True:
        try:
            element = next(elements)
        except StopIteration:
            break
        result += ', ' + prev_element
        prev_element = element
    return result + ' or ' + prev_element

