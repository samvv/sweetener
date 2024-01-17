
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
