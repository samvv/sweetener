
import pytest
from typing import Optional

from .compare import eq
from .record import Record
#from .visual import visualize

def test_record_init_required():

    class MyRecord(Record):
        field_1: str
        field_2: Optional[int]

    r1 = MyRecord('a', 1)
    assert(r1.field_1 == 'a')
    assert(r1.field_2 == 1)

    r2 = MyRecord('b')
    assert(r2.field_1 == 'b')
    assert(r2.field_2 is None)

    with pytest.raises(TypeError):
        MyRecord()

def test_record_init_optional_default():

    class MyRecord(Record):
        field_1: str
        field_2: Optional[int] = 3
        field_3: Optional[str]

    r1 = MyRecord('foo', 'bar')
    assert(r1.field_1 == 'foo')
    assert(r1.field_2 == 3)
    assert(r1.field_3 == 'bar')

    r2 = MyRecord('foo', 'bar', 4)
    assert(r2.field_1 == 'foo')
    assert(r2.field_2 == 4)
    assert(r2.field_3 == 'bar')

    r3 = MyRecord('foo')
    assert(r3.field_1 == 'foo')
    assert(r3.field_2 == 3)
    assert(r3.field_3 is None)

    with pytest.raises(TypeError):
        MyRecord('foo', 'bar', 4, 5)

def test_records_equal():

    class FirstRecord(Record):
        a: int
        b: str

    class SecondRecord(Record):
        a: int
        b: str

    r1 = FirstRecord(1, 'a')

    r2 = FirstRecord(1, 'a')
    assert(eq(r1, r2))

    r3 = SecondRecord(2, 'b')
    assert(not eq(r1, r3))

    r4 = SecondRecord(1, 'a')
    assert(not eq(r1, r4))

