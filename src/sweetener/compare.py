
from typing import Protocol, Self, TypeVar

from .constants import EQUAL_METHOD_NAME
from .util import get_type_index, hasmethod, is_primitive

class _Comparable(Protocol):
    def __lt__(self, other: Self) -> bool: ...

_T = TypeVar('_T')

def lt(v1: _Comparable, v2: _Comparable) -> bool:
    i1 = get_type_index(v1.__class__)
    i2 = get_type_index(v2.__class__)
    if i1 < i2:
        return True
    if i1 == i2:
        # Delegate to Python's built-in comparison method
        return v1 < v2
    return False

def eq(a: _T, b: _T) -> bool:
    if hasmethod(a, EQUAL_METHOD_NAME) and hasmethod(b, EQUAL_METHOD_NAME):
        equal_a_b = getattr(a, EQUAL_METHOD_NAME)
        equal_b_a = getattr(b, EQUAL_METHOD_NAME)
        try:
            return equal_a_b(b)
        except TypeError:
            return equal_b_a(a)
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

def le(v1: _Comparable, v2: _Comparable) -> bool:
    return lt(v1, v2) or eq(v1, v2)

def ge(v1: _Comparable, v2: _Comparable) -> bool:
    return not lt(v1, v2)

def gt(v1: _Comparable, v2: _Comparable) -> bool:
    return not le(v1, v2)

def gte(v1: _Comparable, v2: _Comparable) -> bool:
    return gt(v1, v2) or eq(v1, v2)

def lte(v1: _Comparable, v2: _Comparable) -> bool:
    return lt(v1, v2) or eq(v1, v2)

