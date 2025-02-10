
import pytest

from sweetener.logging import warn
from sweetener.typing import CoerceFn, CoercionError, coerce

def test_coerce_union_str_int_to_int():
    foo: str | int = 1
    assert(coerce(foo, int) == 1)
    with pytest.raises(CoercionError):
        coerce(foo, str)

def test_coerce_union_str_int_to_str():
    foo: str | int = "Hello, world!"
    assert(coerce(foo, str) == "Hello, world!")
    with pytest.raises(CoercionError):
        coerce(foo, int)

def test_coerce_none_to_empty_list():
    assert(coerce(None, list) == [])

def test_coerce_empty_list_to_same_empty_list():
    empty = []
    assert(coerce(empty, list) is empty)

def test_coerce_list_to_same_list():
    l = [ 1, 2, 3 ]
    assert(coerce(l, list) is l)

def test_coerce_fail_int_to_str():
    with pytest.raises(CoercionError):
        coerce(1, str)

def test_coerce_fail_str_to_int():
    with pytest.raises(CoercionError):
        coerce('Hello, world!', int)

def test_coerce_fail_list_to_int():
    with pytest.raises(CoercionError):
        coerce([1, 2, 3], int)

def test_coerce_fail_list_int_to_list_str():
    with pytest.raises(CoercionError):
        print(coerce([ 1, 2, 3 ], list[str]))
