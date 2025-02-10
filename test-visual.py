#!/usr/bin/env python3

from sweetener import visualize, Record, BaseNode


class Foo(Record):
    field_one: str
    field_two: int

foo = Foo('one', 2)

visualize(foo)

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

visualize(prog)
