
import inspect
from typing import Callable, Iterable, Optional, Any, Sequence, Type, TypeVar, cast
from functools import reduce, wraps

_next_type_id = 0
_type_index = dict()

_T = TypeVar('_T')
_A = TypeVar('_A')
_B = TypeVar('_B')

def register_type(ty: Type) -> None:
    global _next_type_id
    index = _next_type_id
    _next_type_id += 1
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
        raise RuntimeError(f"could not determine type index of {ty}: type was not registered during this execution")
    return index

def flatten(l: Iterable[list[_T]]) -> Sequence[_T]:
    return sum(l, [])

foldl = reduce

def get_class_name(value):
    return value.__name__ \
            if type(value) is type \
            else value.__class__.__name__

def flip(func: Callable[[_A, _B], _T]) -> Callable[[_B, _A], _T]:
    @wraps(func)
    def wrapper(x, y):
        return func(y, x)
    return wrapper

def foldr(func: Callable[[_T, _A], _A], xs: Sequence[_T], acc: _A) -> _A:
    for x in reversed(xs):
         acc = func(x, acc)
    return acc

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

type CompareFn[_T] = Callable[[_T, _T], bool]
type WeightFn[_T] = Callable[[_T, _T], int]

def make_comparator(less_than: CompareFn[_T]) -> WeightFn:
    def compare(x, y):
        if less_than(x, y):
            return -1
        if less_than(y, x):
            return 1
        return 0
    return compare

_type_list = [ type(None), bool, int, float, str, tuple, list, dict ]

def lt(v1, v2):
    match (v1, v2):
        case (bool(), bool()):
            return v1 < v2
        case (int(), int()):
            return v1 < v2
        case (float(), float()):
            return v1 < v2
        case (str(), str()):
            return v1 < v2
        case (tuple(), tuple()) | (list(), list()):
            if len(v1) != len(v2):
                return len(v1) < len(v2)
            for el1, el2 in zip(v1, v2):
                if lt(el1, el2):
                    return True
            return False
        case _:
            return _type_list.index(v1.__class__) < _type_list.index(v2.__class__)

def has_method(value, name):
    return hasattr(value, name) \
        and inspect.ismethod(getattr(value, name))

def is_primitive(value):
    return value is None \
        or isinstance(value, str) \
        or isinstance(value, bool) \
        or isinstance(value, float) \
        or isinstance(value, int)


def eq(a, b):
    if has_method(a, 'equal') and has_method(b, 'equal'):
        try:
            return a.equal(b)
        except TypeError:
            return b.equal(a)
    elif is_primitive(a) and is_primitive(b):
        return a == b
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        for el1, el2 in zip(a, b):
            if not eq(el1, el2):
                return False
        return True
    elif isinstance(a, tuple) and isinstance(b, tuple):
        if len(a) != len(b):
            return False
        for el1, el2 in zip(a, b):
            if not eq(el1, el2):
                return False
        return True
    elif isinstance(a, dict) and isinstance(b, dict):
        if len(a) != len(b):
            return False
        for (k_1, v_1), (k_2, v_2) in zip(a.items(), b.items()):
            if not eq(k_1, k_2) or not eq(v_1, v_2):
                return False
        return True
    else:
        return False

def le(v1, v2):
    return lt(v1, v2) or eq(v1, v2)

def ge(v1, v2):
    return not lt(v1, v2)

def gt(v1, v2):
    return not le(v1, v2)

def gte(v1, v2):
    return gt(v1, v2) or eq(v1, v2)

def lte(v1, v2):
    return lt(v1, v2) or eq(v1, v2)

def resolve(value, path: list[Any]):
    for key in path:
        value = value[key]
    return value

def lift_key(proc, path):
    if isinstance(path, str):
        path = path.split('.')
    if not isinstance(path, list):
        path = [ path ]
    def lifted(*args):
        return proc(*(resolve(arg, path) for arg in args))
    return lifted

def nonnull(value: Optional[_T]) -> _T:
    assert(value is not None)
    return value

