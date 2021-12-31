
from typing import List, Any
from functools import reduce, wraps

_next_type_index = 0
_type_index = dict()

def register_type(ty):
    index = _next_type_index
    assert(ty not in _type_index)
    _type_index[ty] = index

for ty in [ type(None), bool, int, float, str, tuple, list, dict ]:
    register_type(ty)

def reflect(target):
    register_type(target)
    return target

def get_type_index(ty):
    index = _type_index.get(ty)
    if index is None:
        raise RuntimeError(f"could not determine type index of {ty}: type was not registered during this session")
    return index

def flatten(l):
    return sum(l, [])

foldl = reduce

def get_class_name(value):
    return value.__name__ \
            if type(value) is type \
            else value.__class__.__name__

def flip(func):
    @wraps(func)
    def newfunc(x, y):
        return func(y, x)
    return newfunc

def foldr(func, xs, acc):
    return reduce(flip(func), reversed(xs), acc)

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

def resolve(value, path: List[Any]):
    for key in path:
        value = value[key]
    return value

def make_comparator(less_than):
    def compare(x, y):
        if less_than(x, y):
            return -1
        elif less_than(y, x):
            return 1
        else:
            return 0
    return compare


def lift_key(proc, path):
    if isinstance(path, str):
        path = path.split('.')
    if not isinstance(path, list):
        path = [ path ]
    def lifted(*args):
        return proc(*(resolve(arg, path) for arg in args))
    return lifted

