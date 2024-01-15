#!/usr/bin/env python3

from sweetener import Record, visualize

class MyRecord(Record):
    field_1: str
    field_2: int

r1 = MyRecord('foo', 42)
visualize(r1)

