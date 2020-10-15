
from typing import List

from .node import *

def test_preorder():
    assert(list(v for v in preorder([1,2,[3,4,[5]],6]) if isinstance(v, int)) == [1,2,3,4,5,6])

class Node(BaseNode):
    pass

class NAry(Node):
    children: List[Node]

class Leaf(Node):
    value: int

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
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    assert(root.first_child == n0)
    assert(root.last_child == n3)
    assert(n0.first_child == n00)
    assert(n0.last_child == n00)
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

    assert(root.next_child is None)
    assert(n00.next_child is None)
    assert(n0.next_child == n1)
    assert(n1.next_child == n2)
    assert(n2.next_child == n3)
    assert(n3.next_child is None)

def test_node_prev_node():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.prev_child is None)
    assert(n0.prev_child is None)
    assert(n00.prev_child is None)
    assert(n1.prev_child == n0)
    assert(n2.prev_child == n1)
    assert(n3.prev_child == n2)

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
