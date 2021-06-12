
from .clazz import hasmethod

def is_empty(iterator):
    try:
        next(iterator)
        return True
    except StopIteration:
        return False

def first(iterator):
    try:
        return next(iterator)
    except StopIteration:
        pass

def last(iterator):
    try:
        last_element = next(iterator)
    except StopIteration:
        return
    for element in iterator:
        last_element = element
    return last_element

def is_iterator(value):
    return hasmethod(value, '__next__')

