
from typing import Any, Iterator, TypeGuard, TypeVar

from .clazz import hasmethod

T = TypeVar('T', covariant=True)

def is_empty(iterator: Iterator[Any]):
    try:
        next(iterator)
        return True
    except StopIteration:
        return False

def first(iterator: Iterator[T]) -> T | None:
    try:
        return next(iterator)
    except StopIteration:
        pass

def last(iterator: Iterator[T]) -> T | None:
    try:
        last_element = next(iterator)
    except StopIteration:
        return
    for element in iterator:
        last_element = element
    return last_element

def is_iterator(value: Any) -> TypeGuard[Iterator[Any]]:
    return hasmethod(value, '__next__')

