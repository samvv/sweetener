
from .clazz import hasmethod
from .common import ischar, isprimitive

_type_indices = [bool, int, float, str, tuple, list]

def lt(v1, v2):
    if isinstance(v1, bool) and isinstance(v2, bool): \
        return v1 < v2
    if isinstance(v1, int) and isinstance(v2, int): \
        return v1 < v2
    if isinstance(v1, float) and isinstance(v2, float): \
        return v1 < v2
    # NOTE We explicitly distinguish between a str and a char because string
    # comparison in python sometimes yields incorrect results.
    if ischar(v1) and ischar(v2):
        return v1 < v2
    elif (isinstance(v1, tuple) and isinstance(v2, tuple)) \
            or (isinstance(v1, list) and isinstance(v2, list)) \
            or (isinstance(v1, str) and isinstance(v2, str)):
        if (len(v1) != len(v2)):
            return len(v1) < len(v2)
        for el1, el2 in zip(v1, v2):
            if lt(el1, el2):
                return True
        return False
    else:
        return _type_indices.index(v1.__class__) < _type_indices.index(v2.__class__)

def eq(a, b):
    if hasmethod(a, 'equal') and hasmethod(b, 'equal'):
        try:
            return a.equal(b)
        except TypeError:
            return b.equal(a)
    elif isprimitive(a) and isprimitive(b):
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

