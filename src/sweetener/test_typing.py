
import pytest

from sweetener.typing import CoercionError, coerce

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

def test_coerce_empty_list_to_empty_list():
    assert(coerce([], list) == [])

def test_coerce_list_to_untyped_list_1():
    l = [ 1, 2, 3 ]
    assert(coerce(l, list) == l)

def test_coerce_list_to_untyped_list_2():
    l = [ 'one', 'two', 'three' ]
    assert(coerce(l, list) == l)

def test_coerce_list_to_untyped_list_3():
    l = [ 1, 'two', 3.3 ]
    assert(coerce(l, list) == l)

def test_coerce_list_to_list_int():
    l = [ 1, 2, 3 ]
    assert(coerce(l, list[int]) == l)

def test_coerce_list_to_list_str():
    l = [ 'one', 'two', 'three' ]
    assert(coerce(l, list[str]) == l)

def test_coerce_list_to_list_union_int_float_str():
    l = [ 1, 'two', 3.3 ]
    assert(coerce(l, list[int | float | str]) == l)

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
        coerce([ 1, 2, 3 ], list[str])

def test_coerce_fail_list_str_to_list_int():
    with pytest.raises(CoercionError):
        coerce([ 'one', 'two', 'three' ], list[int])

def test_coerce_dict_keys():
    res = coerce({ 3: 'Hello', 4.4: 'Bla' }, dict[float, str])
    keys = list(res.keys())
    assert(isinstance(keys[0], float))
    assert(isinstance(keys[1], float))

def test_coerce_dict_values():
    res = coerce({ 'one': 1, 'two': 2.3 }, dict[str, float])
    values = list(res.values())
    assert(isinstance(values[0], float))
    assert(isinstance(values[1], float))

def test_coerce_nested():
    assert(coerce({
        'one': [ { 'x': 1, 'y': 2 } ],
        'two': [ { 'x': 3, 'y': 4 } ],
        'three': [ { 'x': 5, 'y': 6 } ],
    }, dict[str, list[dict[str, float]]]) == {
        'one': [ { 'x': 1.0, 'y': 2.0 } ],
        'two': [ { 'x': 3.0, 'y': 4.0 } ],
        'three': [ { 'x': 5.0, 'y': 6.0 } ],
    })
