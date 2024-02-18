Sweetener
=========

[![Python package](https://github.com/samvv/sweetener/actions/workflows/python-package.yml/badge.svg)](https://github.com/samvv/sweetener/actions/workflows/python-package.yml) [![Coverage Status](https://coveralls.io/repos/github/samvv/sweetener/badge.svg?branch=main)](https://coveralls.io/github/samvv/sweetener?branch=main)

Sweetener is a Python library for quickly prototyping compilers and
interpreters. Extra care has been taken to make the algorithms as flexible as
possible to fit as many use cases. If you're still missing something, do not
hesitate to file an [issue][1]! In particular, this library contains the
following goodies:

 - **A typed record type** that allows you to build PODs very quickly.
 - **Base classes for an AST/CST**, including reflection procedures.
 - **A means for writing diagnostics** that can print part of your source code
   alongside your error messages.
 - **Generic procedures** like `clone`, `equal` and `lte` that work on most
   types in the standard library and you can specialize for your own types.

[1]: https://github.com/samvv/sweetener/issues

## Examples

Here's an example of using the `Record` type to define a record that holds two
fields and visualizes tham using GraphViz:

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

<img src="https://raw.githubusercontent.com/samvv/sweetener/main/sample-record.png" />

```py
from sweetener import BaseNode, visualize

class CalcNode(BaseNode):
    pass

class Expr(CalcNode):
    pass

class Add(Expr):
    left: Expr
    right: Expr

class Sub(Expr):
    left: Expr
    right: Expr

class Var(Expr):
    name: str

class Lit(Expr):
    value: int

prog = Sub(
    Add(
        Lit(1),
        Lit(2)
    ),
    Var('x')
)

def eval(node: Expr, vars = {}) -> int:
    if isinstance(node, Add):
        return eval(node.left, vars) + eval(node.right, vars)
    if isinstance(node, Sub):
        return eval(node.left, vars) - eval(node.right, vars)
    if isinstance(node, Lit):
        return node.value
    if isinstance(node, Var):
        return vars[node.name]
    raise RuntimeError('Could not evaluate a node: unrecognised node type')

assert(eval(prog, { 'x': 3 }) == 0)

visualize(prog, format='png')
```

Running this example will open a new window with the following content:

<img src="https://raw.githubusercontent.com/samvv/sweetener/main/sample-record.png" />

## License

Sweetener is generously licensed under the MIT license, in the hope that it
inspires people to build new and cool software.

