
import pytest

from .ops import resolve, increment_key, decrement_key

def test_path_increment():
    l2 = [5]
    l1 = [3, 4, l2]
    root = [1, 2, l1, 6]
    p0 = []
    assert(resolve(root, p0) == root)
    p1 = increment_key(root, p0)
    assert(resolve(root, p1) == 1)
    p2 = increment_key(root, p1)
    assert(resolve(root, p2) == 2)
    p3 = increment_key(root, p2)
    assert(resolve(root, p3) == l1)
    p4 = increment_key(root, p3)
    assert(resolve(root, p4) == 3)
    p5 = increment_key(root, p4)
    assert(resolve(root, p5) == 4)
    p6 = increment_key(root, p5)
    assert(resolve(root, p6) == l2)
    p7 = increment_key(root, p6)
    assert(resolve(root, p7) == 5)
    p8 = increment_key(root, p7)
    assert(resolve(root, p8) == 6)
    p9 = increment_key(root, p8)
    assert(p9 is None)

def test_path_decrement():
    l2 = [5]
    l1 = [3, 4, l2]
    root = [1, 2, l1, 6]
    p0 = [3]
    assert(resolve(root, p0) == 6)
    p1 = decrement_key(root, p0)
    assert(resolve(root, p1) == 5)
    p2 = decrement_key(root, p1)
    assert(resolve(root, p2) == l2)
    p3 = decrement_key(root, p2)
    assert(resolve(root, p3) == 4)
    p4 = decrement_key(root, p3)
    assert(resolve(root, p4) == 3)
    p5 = decrement_key(root, p4)
    assert(resolve(root, p5) == l1)
    p6 = decrement_key(root, p5)
    assert(resolve(root, p6) == 2)
    p7 = decrement_key(root, p6)
    assert(resolve(root, p7) == 1)
    p8 = decrement_key(root, p7)
    assert(resolve(root, p8) == root)
    p9 = decrement_key(root, p8)
    assert(p9 is None)

