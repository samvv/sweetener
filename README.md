Python Extras Library
======================

This is a library that contains some useful algorithms and data structures that
allow you to be more productive while writing Python code.

## Examples

```
from extralib import Record, equal, visualize

class MySimpleRecord(Record):
  field_1: int
  field_2: str

r1 = MySimpleRecord('foo', 42)
r2 = MySimpleRecod(field_1='foo', field_2=42)

assert(equal(r1, r2))

visualize(r1)
```

Here, `visualize()` will open a new window with the following content:

<img src="https://raw.githubusercontent.com/samvv/python-extralib/master/sample-record.png" />

