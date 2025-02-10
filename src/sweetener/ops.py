
from typing import Any, Callable, Iterable, Protocol, Self, Sequence, TypeVar, cast, overload
from warnings import warn

from sweetener.constants import RESOLVE_METHOD_NAME

from .util import hasmethod, first, last, is_empty

_T = TypeVar('_T')
_K = TypeVar('_K')
_V = TypeVar('_V')
_T_cov = TypeVar('_T_cov', covariant=True)
_T_contra = TypeVar('_T_contra', contravariant=True)

_primitive_types = [ type(None), bool, int, float, str ]

# def clone(value: _T, deep=False) -> _T:
#     if is_primitive(value):
#         return value
#     elif isinstance(value, list):
#         if not deep:
#             return list(value) # type: ignore
#         return list(clone(el, deep=True) for el in value) # type: ignore
#     elif isinstance(value, dict):
#         if not deep:
#             return dict(value) # type: ignore
#         return dict((clone(k, deep=True), clone(v, deep=True)) for (k, v) in value.items()) # type: ignore
#     elif hasmethod(value, 'clone'):
#         return value.clone(deep=deep) # type: ignore
#     else:
#         raise NotImplementedError(f"did not know how to clone {value}")

type ExpandFn = Callable[[Any], Iterable[tuple[Any, Any]]]

@overload
def expand(value: list[_T]) -> Iterable[tuple[int, _T]]: ...

@overload
def expand(value: tuple[_T, ...]) -> Iterable[tuple[int, _T]]: ...

_K_cov = TypeVar('_K_cov', covariant=True)
_V_cov = TypeVar('_V_cov', covariant=True)

class Expandable(Protocol[_K_cov, _V_cov]):
    def _expand(self) -> Iterable[tuple[_K_cov, _V_cov]]: ...

@overload
def expand(value: Expandable[_K_cov, _V_cov]) -> Iterable[tuple[_K_cov, _V_cov]]: ...

def expand(value: Any) -> Iterable[tuple[Any, Any]]:
    if isinstance(value, list) or isinstance(value, tuple):
        for i in range(0, len(value)):
            yield i, value[i]
    elif isinstance(value, dict):
        yield from value.items()
    elif hasmethod(value, '_expand'):
        yield from value._expand()
    else:
        pass

@overload
def resolve(value: Sequence[_T], key: int) -> _T: ...

@overload
def resolve(value: dict[_K, _V], key: _K) -> _V: ...

class Key(Protocol[_T_contra, _T_cov]):
    def _increment(self) -> Self: ...
    def _decrement(self) -> Self: ...
    def _resolve(self, value: _T_contra) -> _T_cov: ...

@overload
def resolve(value: _T_contra, key: Key[_T_contra, _T_cov]) -> _T_cov: ...

@overload
def resolve(value: Any, key: Sequence[Any]) -> Any: ...

def resolve(value: Any, key: Any) -> Any:
    if hasmethod(key, RESOLVE_METHOD_NAME):
        method = getattr(key, RESOLVE_METHOD_NAME)
        return method(value)
    if isinstance(key, list):
        result = value
        for element in key:
            result = resolve(result, element)
        return result
    if isinstance(key, int) or isinstance(key, str):
        return value[key]
    raise TypeError(f'could not determine how to resolve a value with key {key}')

def erase(value: Any, key: Any) -> None:
    if isinstance(key, int) \
            or isinstance(key, str):
        del value[key]
    elif isinstance(key, list):
        child = resolve(value, key[:-1])
        erase(child, key[-1])
    else:
        raise RuntimeError(f'did not know how to erase from key {key}')

def increment_key(value: Any, key: Any, expand=expand) -> Any | None:

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
            keys = iter(value.keys())
            for k in keys:
                if k == key:
                    break
            try:
                return next(keys)
            except StopIteration:
                return None

        case _:
            raise RuntimeError(f'did not know how to increment key {key}')

def decrement_key(value: Any, key: Any, expand=expand) -> Any:

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

def lift_key(proc: Callable[..., Any], path: Any) -> Callable[..., Any]:
    if isinstance(path, str):
        path = path.split('.')
    if not isinstance(path, list):
        path = [ path ]
    def lifted(*args):
        return proc(*(resolve(arg, path) for arg in args))
    return lifted

class Clonable(Protocol):
    def clone(self) -> Self: ...

def clone(value: _T, deep = False) -> _T:

    for cls in _primitive_types:
        if isinstance(value, cls):
            return value

    if hasmethod(value, 'clone'):
        return cast(_T, getattr(value, 'clone'))

    if isinstance(value, dict):
        return cast(_T, dict((k, clone(v, True) if deep else v) for k, v in value.items()))

    if isinstance(value, list):
        return cast(_T, list(clone(el, True) if deep else el for el in value))

    if isinstance(value, tuple):
        return cast(_T, tuple(clone(el, True) if deep else el for el in value))

    if isinstance(value, set):
        return cast(_T, set(clone(el, True) if deep else el for el in value))

    raise RuntimeError(f'could not clone {value} becaue it did not have a .clone() and was not recognised as a primitive type')

