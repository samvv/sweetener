
from .sorting import isheap, isheap, heapsort, heapify

def test_isheap_last_element_greater():
    l1 = [4,3,2,5]
    assert(isheap(l1) == False)
    l2 = [4,3,2,1]
    assert(isheap(l2) == True)
    l3 = [4,3,2,1,5]
    assert(isheap(l3) == False)
    l4 = [5,4,3,2,1]
    assert(isheap(l4) == True)
    l5 = [5,4,3,2,1,6]
    assert(isheap(l5) == False)
    l6 = [6,5,4,3,2,1]
    assert(isheap(l6) == True)

def test_isheap_first_element_smaller():
    l1 = [0,3,2,1]
    assert(isheap(l1) == False)
    l2 = [3,2,1,0]
    assert(isheap(l2) == True)
    l3 = [0,4,3,2,1]
    assert(isheap(l3) == False)
    l4 = [4,3,2,1,0]
    assert(isheap(l4) == True)
    l5 = [0,5,4,3,2,1]
    assert(isheap(l5) == False)
    l6 = [5,4,3,2,1,0]
    assert(isheap(l6) == True)

def test_heapsort_reverse_incremental():
    l = [4,3,2,1]
    heapsort(l)
    assert(l[0] == 1)
    assert(l[1] == 2)
    assert(l[2] == 3)
    assert(l[3] == 4)

def test_heapify_random_list():
    l = [6, 2, 5, 3, 8, 9, 10, 4, 7, 1]
    assert(isheap(l) == False)
    heapify(l)
    print(l)
    assert(isheap(l) == True)

def test_heapsort_random_list():
    l = [6, 2, 5, 3, 8, 9, 10, 4, 7, 1]
    assert(isheap(l) == False)
    heapsort(l)
    assert(l[0] == 1)
    assert(l[1] == 2)
    assert(l[2] == 3)
    assert(l[3] == 4)
    assert(l[4] == 5)
    assert(l[5] == 6)
    assert(l[6] == 7)
    assert(l[7] == 8)
    assert(l[8] == 9)

