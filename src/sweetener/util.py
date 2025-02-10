
import inspect
from typing import Callable, Iterable, Iterator, Optional, Any, Protocol, Sequence, TypeGuard, TypeIs, TypeVar
from functools import reduce, wraps

_next_type_id = 0
_type_index = dict()

primitive_types = [ type(None), bool, int, float, complex, str ]

def register_type(ty: type) -> None:
    global _next_type_id
    index = _next_type_id
    _next_type_id += 1
    assert(ty not in _type_index)
    _type_index[ty] = index

for ty in [ type(None), bool, int, float, complex, str, tuple, list, dict ]:
    register_type(ty)

_Class = TypeVar('_Class', bound=type)

def reflect(target: _Class) -> _Class:
    """
    A decorator to register this class for reflection.

    Through reflection data can e.g. be deserialized into the class.
    """
    register_type(target)
    return target

def get_type_index(ty: type) -> int:
    index = _type_index.get(ty)
    if index is None:
        raise RuntimeError(f"could not determine type index of {ty}: type was not registered during this execution")
    return index

_T = TypeVar('_T')
_A = TypeVar('_A')
_B = TypeVar('_B')

def flatten(l: Iterable[list[_T]]) -> Sequence[_T]:
    return sum(l, [])

foldl = reduce

def get_class_name(value: Any) -> str:
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

class _ToStr(Protocol):
    def __str__(self) -> str: ...

def pretty_enumerate(elements: Iterable[_ToStr], default='nothing') -> str:
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
        result += ', ' + str(prev_element)
        prev_element = element
    return result + ' or ' + str(prev_element)

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

def has_method(value, name):
    return hasattr(value, name) \
        and inspect.ismethod(getattr(value, name))

type Primitive = bool | int | float | str | None

def is_primitive(value: Any) -> TypeIs[Primitive]:
    # TODO Add complex and other types
    return value is None \
        or isinstance(value, str) \
        or isinstance(value, bool) \
        or isinstance(value, float) \
        or isinstance(value, int)

def is_char(value: Any) -> TypeGuard[str]:
    return isinstance(value, str) \
        and len(value) == 1

def nonnull(value: Optional[_T]) -> _T:
    assert(value is not None)
    return value

def hasmethod(value: Any, name: str) -> bool:
    return hasattr(value, name) \
        and callable(getattr(value, name))

def is_empty(iterator: Iterator[Any]) -> bool:
    try:
        next(iterator)
        return True
    except StopIteration:
        return False

def first(iterator: Iterator[_T]) -> _T | None:
    try:
        return next(iterator)
    except StopIteration:
        pass

def last(iterator: Iterator[_T]) -> _T | None:
    try:
        last_element = next(iterator)
    except StopIteration:
        return
    for element in iterator:
        last_element = element
    return last_element

def is_iterator(value: Any) -> TypeGuard[Iterator[Any]]:
    return hasmethod(value, '__next__')


