
from collections import deque
from typing import Generator, Literal

from .iterator import first, last
from .record import Record
from .ops import expand, increment_key, decrement_key, resolve, erase

type Path = list[str | int]

type Unassigned = Literal[False]

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
        self.parent: BaseNode | None = None
        self.path: Path | None = None
        self._prev_sibling: BaseNode | None | Unassigned = False
        self._next_sibling: BaseNode | None | Unassigned = False

    def get_full_path(self):
        path = []
        node = self
        while True:
            assert(node.path is not None)
            path.extend(reversed(node.path))
            node = node.parent
            if node is None:
                break
        path.reverse()
        return path

    @property
    def prev_sibling(self) -> 'BaseNode | None':
        if self._prev_sibling != False:
            return self._prev_sibling
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
        self._prev_sibling = node
        if node is not None:
            node._next_sibling = self
        return node

    @property
    def next_sibling(self) -> 'BaseNode | None':
        if self._next_sibling != False:
            return self._next_sibling
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
        self._next_sibling = node
        return node

    def remove(self) -> None:
        if self._prev_sibling:
            self._prev_sibling._next_sibling = self.next_sibling
        if self._next_sibling:
            self._next_sibling._prev_sibling = self.prev_sibling
        if self.parent is not None:
            for field_name, field_value in self.parent.fields.items():
                # TODO make use of self.path
                for path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
                    if child == self:
                        path.insert(0, field_name)
                        value = resolve(self.parent, path[:-1])
                        erase(value, path[-1])

    def replace_with(self, new_node: 'BaseNode') -> None:
        new_node.parent = self.parent
        new_node.path = self.path
        if self._prev_sibling:
            self._prev_sibling._next_sibling = new_node
        if self._next_sibling:
            self._next_sibling._prev_sibling = new_node
        if self.parent is not None:
            for field_name, field_value in self.parent.fields.items():
                for path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
                    if child == self:
                        path.insert(0, field_name)
                        value = resolve(self.parent, path[:-1])
                        value[path[-1]] = new_node

    @property
    def first_child(self) -> 'BaseNode | None':
        return first(self.get_child_nodes())

    @property
    def last_child(self) -> 'BaseNode | None':
        return last(self.get_child_nodes())

    def get_all_child_nodes(self) -> Generator['BaseNode', None, None]:
        for field_value in self.fields.values():
            for child in preorder(field_value):
                if isinstance(child, BaseNode):
                    yield child

    def get_child_nodes(self) -> Generator['BaseNode', None, None]:
        for field_value in self.fields.values():
            for child in preorder(field_value, expand=expand_no_basenode):
                if isinstance(child, BaseNode):
                    yield child

def expand_no_basenode(value):
    if not isinstance(value, BaseNode):
        yield from expand(value)

def set_parent_nodes(node: BaseNode, parent: BaseNode | None = None, path: Path = []) -> None:
    node.parent = parent
    node.path = path
    for field_name, field_value in node.fields.items():
        for new_path, child in preorder_with_paths(field_value, expand=expand_no_basenode):
            if isinstance(child, BaseNode):
                new_path.insert(0, field_name)
                set_parent_nodes(child, node, new_path)

