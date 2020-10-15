
from collections import deque

from .util import first, last
from .record import Record
from .ops import clone, expand, increment_key, decrement_key, resolve, erase

def breadthfirst(root, expand):
    queue = deque([ root ])
    while len(queue) > 0:
        node = queue.popleft()
        yield node
        for node in reversed(list(expand(node))):
            queue.append(node)

def preorder(root, expand=expand):
    stack = [ root ]
    while stack:
        node = stack.pop()
        yield node
        for _key, value in reversed(list(expand(node))):
            stack.append(value)

def preorder_with_paths(root, expand=expand):
    stack = [ ([], root) ]
    while stack:
        path, node = stack.pop()
        yield path, node
        for key, value in expand(node):
            stack.append((path + [key], value))

def postorder(root, expand):
    stack_1 = [root]
    stack_2 = []
    while stack_1:
        node = stack_1.pop()
        stack_2.append(node)
        for child in reversed(list(expand(node))):
            stack_1.append(child)
    for node in reversed(stack_2):
        yield node

class BaseNode(Record):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None
        self.path = None
        self._prev_child = False
        self._next_child = False

    def get_full_path(self):
        path = []
        node = self
        while node is not None:
            for element in reversed(node.path.elements):
                path.append(element)
        path.reverse()
        return path

    @property
    def prev_child(self):
        if self._prev_child != False:
            return self._prev_child
        path = self.path
        while True:
            path = decrement_key(self.parent, path, expand=expand_no_basenode)
            if not path:
                return None
            value = resolve(self.parent, path)
            if isinstance(value, BaseNode):
                node = value
                # while node.last_child:
                #     node = node.last_child
                break
        self._prev_child = node
        if node is not None:
            node._next_child = self
        return node

    @property
    def next_child(self):
        if self._next_child != False:
            return self._next_child
        node = self.parent
        path = self.path
        while True:
            if node is None:
                return None
            path = increment_key(node, path, expand=expand_no_basenode)
            if path is None:
                return None
                # path = node.path
                # node = node.parent
            else:
                value = resolve(node, path)
                if isinstance(value, BaseNode):
                    node = value
                    break
        self._next_child = node
        return node

    def remove(self):
        if self._prev_child:
            self._prev_child._next_child = self.next_child
        if self._next_child:
            self._next_child._prev_child = self.prev_child
        if self.parent is not None:
            for field_name, field_value in self.parent.items():
                for path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
                    if child == self:
                        path.insert(0, field_name)
                        value = resolve(self.parent, path[:-1])
                        erase(value, path[-1])

    def replace_with(self, new_node):
        new_node.parent = self.parent
        new_node.path = self.path
        if self._prev_child:
            self._prev_child._next_child = new_node
        if self._next_child:
            self._next_child._prev_child = new_node
        if self.parent is not None:
            for field_name, field_value in self.parent.items():
                for path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
                    if child == self:
                        path.insert(0, field_name)
                        value = resolve(self.parent, path[:-1])
                        value[path[-1]] = new_node

    @property
    def first_child(self):
        return first(self.get_child_nodes())

    @property
    def last_child(self):
        return last(self.get_child_nodes())

    def get_child_nodes(self):
        for _field_name, field_value in self.items():
            for child in preorder(field_value, expand=expand_no_basenode):
                if isinstance(child, BaseNode):
                    yield child

def expand_no_basenode(value):
    if not isinstance(value, BaseNode):
        yield from expand(value)

def set_parent_nodes(node, parent=None, path=[]):
    node.parent = parent
    node.path = path
    for field_name, field_value in node.items():
        for new_path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
            if isinstance(child, BaseNode):
                new_path.insert(0, field_name)
                set_parent_nodes(child, node, new_path)

