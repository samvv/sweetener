Sweetener
=========

[![Build Status](https://travis-ci.org/samvv/Sweetener.svg?branch=master)](https://travis-ci.org/samvv/Sweetener)

Sweetener is a Python library that contains some generic algorithms and data
structures not found in the standard libary. Extra care has been taken to make
the algorithms as flexible as possible to fit as many use cases. If you're
still missing something, do not hesitate to file an [issue][1]!

In particular, this library contains the following goodies:

  - **Generic procedures** like `clone`, `equal` and `lte` that work on most
    types in the standard library and you can specialize for your own types.
  - A **typed record type** that allows you to very quickly define a new data
    structure with some built-in validation.
  - A **generic representation for parse trees** that allows you to define,
    query and manipulate individual nodes with ease.

[1]: https://github.com/samvv/Sweetener/issues

## Examples

```py
from sweetener import Record, equal, visualize

class MySimpleRecord(Record):
    field_1: int
    field_2: str

r1 = MySimpleRecord('foo', 42)
r2 = MySimpleRecod(field_1='foo', field_2=42)

assert(equal(r1, r2))

visualize(r1)
```

Running this program will open a new window with the following content:

<img src="https://raw.githubusercontent.com/samvv/Sweetener/master/sample-record.png" />

## License

Sweetener is generously licensed under the MIT license, in the hope that it
inspires people to build new and cool software.

