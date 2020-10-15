
from .util import has_method, is_primitive, first, last, is_empty

def clone(value, deep=False):
    if is_primitive(value):
        return value
    elif isinstance(value, list):
        if not deep:
            return list(value)
        return list(clone(el, deep=True) for el in value)
    elif isinstance(value, dict):
        if not deep:
            return dict(value)
        return dict((clone(k, deep=True), clone(v, deep=True)) for (k, v) in value.items())
    elif has_method(value, 'clone'):
        return value.clone(deep=deep)
    else:
        raise NotImplementedError(f"did not know how to clone {value}")

def equal(a, b):
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
            if not equal(el1, el2):
                return False
        return True
    elif isinstance(a, dict) and isinstance(b, dict):
        if len(a) != len(b):
            return False
        for (k1, v1), (k2, v2) in zip(a.items(), b.items()):
            if not equal(k1, k2) or not equal(v1, v2):
                return False
        return True
    else:
        raise TypeError(f'values {a} and {b} are not comparable')

def expand(value):
    if isinstance(value, list) or isinstance(value, tuple):
        for i in range(0, len(value)):
            yield i, value[i]
    elif isinstance(value, dict):
        yield from value.items()
    elif has_method(value, 'expand'):
        yield from value.expand()
    else:
        pass

def resolve(value, key):
    if has_method(key, 'resolve'):
        return key.resolve(value)
    if isinstance(key, list):
        result = value
        for element in key:
            result = resolve(result, element)
        return result
    elif isinstance(key, int) or isinstance(key, str):
        return value[key]
    else:
        raise TypeError(f'could not determine how to resolve key {key}')

def erase(value, key):
    if isinstance(key, int) \
            or isinstance(key, str):
        del value[key]
    elif isinstance(key, list):
        child = resolve(value, key[-1])
        erase(child, key[-1])
    else:
        raise RuntimeError(f'did not know how to erase from key {key}')

def increment_key(value, key, expand=expand):

    if has_method(key, 'increment'):
        return key.increment(value)

    elif isinstance(key, list):

        # pre-populate a list of child nodes of self.root so we can access them
        # easily
        values = [ value ]
        for element in key:
            value = resolve(value, element)
            values.append(value)

        # if we still can go deeper we should try that first
        result = first(expand(value))
        if result is not None:
            element, _child = result
            new_key = clone(key)
            new_key.append(element)
            return new_key

        # go up until we find a key that we can increment
        for i in reversed(range(0, len(key))):
            element = key[i]
            new_element = increment_key(values[i], element)
            if new_element is not None:
                new_key = key[:i]
                new_key.append(new_element)
                return new_key

        # we went up beyond the root node
        return None

    elif isinstance(key, int):
        return key+1 if key < len(value)-1 else None

    elif isinstance(key, str):
        items = iter(value.items())
        for k, _v in items:
            if k == key:
                break
        try:
            return next(items)[0]
        except StopIteration:
            return None

    raise RuntimeError(f'did not know how to increment key {key}')

def decrement_key(value, key, expand=expand):

    if has_method(key, 'decrement'):
        return key.decrement(value)

    elif isinstance(key, list):

        # pre-populate a list of child nodes of self.root so we can access them
        # easily
        last_value_parent = None
        for element in key:
            last_value_parent = value
            value = resolve(value, element)

        if not key:
            return None

        last_element = key[-1]
        new_element = decrement_key(last_value_parent, last_element)

        if new_element is None:
            return key[:-1]

        new_key = key[:-1]
        new_key.append(new_element)

        # get the rightmost node relative to the node on the new key
        value = resolve(last_value_parent, new_element)
        while True:
            result = last(expand(value))
            if result is None:
                break
            child_key, value = result
            # self.elements.append(child_key)
            new_key.append(child_key)

        return new_key

    elif isinstance(key, int):
        return key-1 if key > 0 else None

    elif isinstance(key, str):
        last_key = None
        for k, _v in value.items():
            if k == key:
                break
            last_key = k
        return last_key

    else:
        raise RuntimeError(f'did not know how to decrement key {key}')

TYPE_INDICES = [bool, int, float, str, tuple, list]

def is_char(v):
    return isinstance(v, str) and len(v) == 1

# NOTE We explicitly distinguish between a str and a char because string
# comparison in python sometimes yields incorrect results.
def lt(v1, v2):
    if (isinstance(v1, bool) and isinstance(v2, bool)) \
            or (isinstance(v1, int) and isinstance(v2, int)) \
            or (isinstance(v1, float) and isinstance(v2, float)) \
            or (is_char(v1) and is_char(v2)):
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
        return TYPE_INDICES.index(v1.__class__) < TYPE_INDICES.index(v2.__class__)

def lte(v1, v2):
    return lt(v1, v2) or equal(v1, v2)

def gte(v1, v2):
    return not lt(v1, v2)

def gt(v1, v2):
    return not lte(v1, v2)

# def is_expandable(value):
#     return isinstance(value, list) \
#         or isinstance(value, tuple) \
#         or isinstance(value, dict) \
#         or has_method(value, 'expand')

def is_iterator(value):
    return has_method(value, '__next__')

def is_first_key(root, key):
    if isinstance(key, list):
        return len(key) == 0

def is_last_key(root, key):

    if isinstance(key, int):
        return key == len(root)-1

    elif isinstance(key, list):

        # pre-populate a list of child nodes of self.root so we can access them
        # easily
        value = root
        values = [ value ]
        for element in key:
            value = resolve(value, element)
            values.append(value)

        # if we still can go deeper we should try that first
        if not is_empty(expand(value)):
            return False

        # go up until we find a key that we can increment
        for i in reversed(range(0, len(key))):
            element = key[i]
            new_element = increment_key(values[i], element)
            if new_element is not None:
                return False

        # we were unable to find a new path, so this must be the end
        return True

    else:
        raise TypeError(f'key {key}')
