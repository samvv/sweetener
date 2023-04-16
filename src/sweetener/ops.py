
from typing import TypeVar

from .clazz import hasmethod
from .common import isprimitive
from .iterator import first, last, is_empty

T = TypeVar('T')

def clone(value: T, deep=False) -> T:
    if isprimitive(value):
        return value
    elif isinstance(value, list):
        if not deep:
            return list(value) # type: ignore
        return list(clone(el, deep=True) for el in value) # type: ignore
    elif isinstance(value, dict):
        if not deep:
            return dict(value) # type: ignore
        return dict((clone(k, deep=True), clone(v, deep=True)) for (k, v) in value.items()) # type: ignore
    elif hasmethod(value, 'clone'):
        return value.clone(deep=deep) # type: ignore
    else:
        raise NotImplementedError(f"did not know how to clone {value}")

def expand(value):
    if isinstance(value, list) or isinstance(value, tuple):
        for i in range(0, len(value)):
            yield i, value[i]
    elif isinstance(value, dict):
        yield from value.items()
    elif hasmethod(value, 'expand'):
        yield from value.expand()
    else:
        pass

def resolve(value, key):
    if hasmethod(key, 'resolve'):
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

    if hasmethod(key, 'increment'):
        return key.increment(value)

    match key:

        case list():

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

        case int():
            return key+1 if key < len(value)-1 else None

        case str():
            items = iter(value.items())
            for k, _v in items:
                if k == key:
                    break
            try:
                return next(items)[0]
            except StopIteration:
                return None

        case _:
            raise RuntimeError(f'did not know how to increment key {key}')

def decrement_key(value, key, expand=expand):

    if hasmethod(key, 'decrement'):
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

# def is_expandable(value):
#     return isinstance(value, list) \
#         or isinstance(value, tuple) \
#         or isinstance(value, dict) \
#         or hasmethod(value, 'expand')

def is_first_key(root, key):
    if isinstance(key, list):
        return not key
    elif isinstance(key, int):
        return key == 0
    else:
        raise TypeError(f'key {key}')

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

