
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

def test_node_next_node():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.next_node == n0)
    assert(n0.next_node == n00)
    assert(n00.next_node == n1)
    assert(n1.next_node == n2)
    assert(n2.next_node == n3)
    assert(n3.next_node is None)

def test_node_prev_node():

    n00 = Leaf(0)
    n0 = NAry([ n00 ])
    n1 = Leaf(1)
    n2 = Leaf(2)
    n3 = Leaf(3)
    root = NAry([ n0, n1, n2, n3 ])

    set_parent_nodes(root)

    assert(root.prev_node is None)
    assert(n0.prev_node == root)
    assert(n00.prev_node == n0)
    assert(n1.prev_node == n00)
    assert(n2.prev_node == n1)
    assert(n3.prev_node == n2)

