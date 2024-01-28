
from typing import List

from .node import *

def test_preorder():
    assert(list(v for v in preorder([1,2,[3,4,[5]],6]) if isinstance(v, int)) == [1,2,3,4,5,6])

class Node(BaseNode):
    pass

class NAry(Node):
    children: List[Node]

class Leaf(Node):
    value: int | str

class Matrix(Node):
    elements: list[list[Node]]

def test_node_set_parent_nodes():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.parent is None)
    assert(n0.parent == root)
    assert(n1.parent == root)
    assert(n2.parent == root)
    assert(n3.parent == root)
    assert(n00.parent == n0)

def test_node_first_last_property():

    n00 = Leaf(0)
    n010 = Leaf(1)
    n01 = NAry([ n010 ])
    n0 = NAry([ n00, n01 ])
    n1 = Leaf(2)
    n2 = Leaf(3)
    n3 = Leaf(4)
    root = NAry([ n0, n1, n2, n3 ])

    assert(root.first_child == n0)
    assert(root.last_child == n3)
    assert(n01.first_child == n010)
    assert(n01.last_child == n010)
    assert(n0.first_child == n00)
    assert(n0.last_child == n01)
    assert(n00.first_child is None)
    assert(n00.last_child is None)

def test_node_next_child():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.next_sibling is None)
    assert(n00.next_sibling is None)
    assert(n0.next_sibling == n1)
    assert(n1.next_sibling == n2)
    assert(n2.next_sibling == n3)
    assert(n3.next_sibling is None)

def test_node_prev_child():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.prev_sibling is None)
    assert(n0.prev_sibling is None)
    assert(n00.prev_sibling is None)
    assert(n1.prev_sibling == n0)
    assert(n2.prev_sibling == n1)
    assert(n3.prev_sibling == n2)

def test_replace_with_node():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    n4 = Leaf(4)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    n00.replace_with(n4)

    assert(n4.parent == n0)
    assert(n0.first_child == n4)
    assert(n0.last_child == n4)
    assert(n0.children[0] == n4)

def test_remove_node():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    n00.remove()

    assert(len(n0.children) == 0)

    n2.remove()
    assert(n3.next_sibling == None)
    assert(n1.prev_sibling == n0)
    assert(n1.next_sibling == n3)
    assert(n3.prev_sibling == n1)
    assert(len(root.children) == 3)
    assert(root.children[0] == n0)
    assert(root.children[1] == n1)
    assert(root.children[2] == n3)

def test_remove_node_nested():

    n00 = Leaf('00')
    n01 = Leaf('01')
    n02 = Leaf('02')
    n10 = Leaf('10')
    n11 = Leaf('11')
    n12 = Leaf('12')

    m = Matrix([
        [ n00, n01, n02 ],
        [ n10, n11, n12 ],
    ])

    set_parent_nodes(m)

    n01.remove()

    assert(m.elements[0][0] == n00)
    assert(m.elements[0][1] == n02)
    assert(m.elements[1][0] == n10)
    assert(m.elements[1][1] == n11)
    assert(m.elements[1][2] == n12)

    for row in m.elements:
        for cell in row:
            assert(resolve(m, cell.parent_path) == cell)

def test_get_full_path():

    n00 = Leaf(0)
    n0 = Leaf(1)
    n1 = NAry([ n00 ])
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    p = n00.get_full_path()
    assert(p[0] == 'children')
    assert(p[1] == 1)
    assert(p[2] == 'children')
    assert(p[3] == 0)

