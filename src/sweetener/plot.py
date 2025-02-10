
from enum import IntEnum
import inspect
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Protocol, TypeIs, assert_never

from sweetener.logging import warn
from sweetener.util import nonnull

try:
    import graphviz
except ImportError:
    graphviz = None

from .record import Record, satisfies_type
from .util import is_primitive

class Direction(IntEnum):
    HORIZONTAL = 1
    VERTICAL   = 2

    def invert(self):
        if self == Direction.HORIZONTAL:
            return Direction.VERTICAL
        elif self == Direction.VERTICAL:
            return Direction.HORIZONTAL

type PlotElement = PlotNode | PlotEdge | PlotCells | PlotText

type PlotInline = PlotCells | PlotText

type PlotToplevel = PlotNode | PlotEdge

def is_plot_element(value: Any) -> TypeIs[PlotElement]:
    return isinstance(value, PlotElementBase)

_graphs_dir = Path('.pygraphs')

_plotters = list[Callable[['Plotter', Any], PlotElement]]()

def _plot_record(plotter: 'Plotter', record: Record) -> 'PlotElement':
    label = PlotCells(direction=Direction.VERTICAL)
    label.add_text(record.__class__.__name__, key='__name__')
    node = plotter.add_node(label=label, shape='record')
    for (key, value) in record.fields.items():
        p = plotter.plot(value)
        if p.is_embeddable:
            row = label.add_cells(direction=Direction.HORIZONTAL, key=f'field-{key}')
            row.add_text(key)
            row.add_element(p)
        else:
            plotter.add_edge(node, p, label=key)
    return node

PLOT_METHOD_NAME = '_plot'

class Plottable(Protocol):
    def _plot(self, plotter: 'Plotter', key: str | None = None) -> 'PlotElement': ...

def _plot_plottable(plotter: 'Plotter', value: Plottable, key: str | None = None) -> 'PlotElement':
    method = getattr(value, PLOT_METHOD_NAME)
    return method(plotter, key)

_plotters.append(_plot_record)
_plotters.append(_plot_plottable)

def encode(value: Any) -> Any:
    if is_primitive(value):
        return value
    if isinstance(value, list):
        return list(encode(element) for element in value)
    if isinstance(value, dict):
        return dict((encode(k), encode(v)) for k, v in value.items())
    if is_plot_element(value):
        return value._to_dict()
    raise NotImplementedError(f'{value}')

class PlotElementBase:

    is_embeddable: bool
    """
    Whether this element is 'embedded' into the parent element.
    """

    def __init__(self, key: str | None) -> None:
        self.key = key
        self.id: str | None = None

    def _to_dict(self) -> dict[str, Any]:
        out = dict[str, Any]()
        out['__name__'] = self.__class__.__name__
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                out[k] = encode(v)
        return out

    def __repr__(self) -> str:
        from pprint import PrettyPrinter
        out = StringIO()
        printer = PrettyPrinter(stream=out)
        printer.pprint(self._to_dict())
        return out.getvalue()

class PlotNode(PlotElementBase):

    is_embeddable = False

    def __init__(
        self,
        label: PlotInline,
        bg_color='transparent',
        fg_color='black',
        shape='circle',
        key: str | None = None
    ) -> None:
        super().__init__(key)
        self.label = label
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.shape = shape

class PlotCells(PlotElementBase):

    is_embeddable = True

    def __init__(self, direction = Direction.HORIZONTAL, key: str | None = None) -> None:
        super().__init__(key)
        self.direction = direction
        self.children = []

    def add_element(self, element) -> None:
        self.children.append(element)

    def add_cells(self, *args, **kwargs) -> 'PlotCells':
        cells = PlotCells(*args, **kwargs)
        self.children.append(cells)
        return cells

    def add_text(self, *args, **kwargs) -> 'PlotText':
        text = PlotText(*args, **kwargs)
        self.children.append(text)
        return text

class PlotText(PlotElementBase):

    is_embeddable = True

    def __init__(self, text, key=None) -> None:
        super().__init__(key)
        self.text = str(text)

class PlotEdge(PlotElementBase):

    is_embeddable = False

    def __init__(self, a: PlotElement, b: PlotElement, label=None, key=None) -> None:
        super().__init__(key)
        self.a = a
        self.b = b
        self.label = label

class Plotter:

    def __init__(self) -> None:
        self._next_node_id = 0
        self.visited = dict[Any, PlotElement]()
        self.children = list[PlotToplevel]()

    def _generate_id(self) -> str:
        id = self._next_node_id
        self._next_node_id += 1
        return str(id)

    def add_node(self, *args, **kwargs) -> 'PlotNode':
        node = PlotNode(*args, **kwargs)
        self.children.append(node)
        return node

    def add_edge(self, *args, **kwargs) -> 'PlotEdge':
        edge = PlotEdge(*args, **kwargs)
        self.children.append(edge)
        return edge

    def _plot_external(self, value: Any) -> PlotElement:
        for proc in _plotters:
            sig = inspect.signature(proc)
            params = list(sig.parameters.values())
            ty = params[1].annotation
            if satisfies_type(value, ty):
                return proc(self, value)
        raise RuntimeError(f"did not know how to plot {value}")

    def plot(self, value: Any) -> PlotElement:
        if is_primitive(value):
            return PlotText(str(value))
        elif isinstance(value, list):
            table = PlotCells(direction=Direction.VERTICAL)
            for i, child in enumerate(value):
                p = self.plot(child)
                if isinstance(child, list):
                    keep = p
                    p = table.add_cells(direction=Direction.HORIZONTAL)
                    p.add_element(PlotText(str(i)))
                    p.add_element(keep) # TODO test if keep.is_embeddable
                elif p.is_embeddable:
                    table.add_element(p)
                else:
                    text = table.add_text(str(i))
                    self.add_edge(text, p)
            return table
        # elif isinstance(value, tuple):
        #     table = PlotCells(direction=Direction.VERTICAL)
        #     row = table.add_cells(direction=Direction.HORIZONTAL)
        #     for i, child in enumerate(value):
        #         # TODO check p.is_embeddable
        #         p = self.plot(child)
        #         row.add_element(p)
        #     return table
        # elif isinstance(value, dict):
        #     table = PlotCells(direction=Direction.VERTICAL)
        #     for i, (k, v) in enumerate(value.items()):
        #         # TODO check p{1,2}.is_embeddable
        #         p1 = self.plot(k)
        #         p2 = self.plot(v)
        #         row = table.add_cells(direction=Direction.HORIZONTAL)
        #         row.add_element(p1)
        #         row.add_element(p2)
        #     return table
        else:
            if value in self.visited:
                return self.visited[value]
            element = self._plot_external(value)
            self.visited[value] = element
            return element

def visualize(value: Any, name: str | None = None, format: str | None = None, view = True) -> None:

    if graphviz is None:
        warn("Package 'graphviz' is not installed. Install it with pip install --user -U graphviz")
        return

    if isinstance(value, Plotter):
        plotter = value
    else:
        plotter = Plotter()
        plotter.plot(value)

    next_id = 0

    def generate_id() -> str:
        nonlocal next_id
        id = str(next_id)
        next_id += 1
        return id

    visited = set[PlotElement]()

    def assign_inline_ids(element: PlotInline, parent_id: str) -> None:
        element.id = parent_id + ':' + generate_id()
        if isinstance(element, PlotCells):
            for child in element.children:
                assign_inline_ids(child, parent_id)
        elif isinstance(element, PlotText):
            pass
        else:
            raise NotImplementedError(f"did not know how to update IDs of {element}")

    def assign_ids(element: PlotElement) -> None:
        if element in visited:
            return
        visited.add(element)
        element.id = generate_id()
        if isinstance(element, PlotNode):
            assign_inline_ids(element.label, element.id)
        elif isinstance(element, PlotEdge):
           pass
        else:
            raise NotImplementedError(f"did not know how to update IDs of {element}")

    for child in plotter.children:
        assign_ids(child)

    _graphs_dir.mkdir(parents=True, exist_ok=True)
    if name is None:
        i = len(list(_graphs_dir.iterdir()))
        filename = _graphs_dir / f"temp{i}.gv"
    else:
        filename = _graphs_dir / f"{name}.gv"

    dot = graphviz.Digraph(filename=filename)

    # Emit the graph using the graphviz library

    nodes = list[tuple[str, str, str, str]]()
    edges = list[tuple[str, str, str | None]]()

    def escape(text: str) -> str:
        out = ''
        for ch in text:
            if not ch.isprintable():
                out += f'\\x{ord(ch):02x}';
                continue
            if ord(ch) > 0x7F:
                out += f'&#{ord(ch)};'
                continue
            if ch in [ '"', '{', '\\', '>', '<' ]:
                out += '\\'
            out += ch
        return out

    def emit_label(element: PlotInline, curr_direction = Direction.HORIZONTAL) -> str:
        if isinstance(element, PlotText):
            return escape(element.text)
        if isinstance(element, PlotCells):
            out = ''
            if element.direction != curr_direction:
                out += '{'
            if element.children:
                out += ' '
                for i, child in enumerate(element.children):
                    if i > 0: out += ' | '
                    if isinstance(child, PlotText):
                        id = nonnull(child.id)
                        chunks = id.split(':')
                        assert(len(chunks) == 2)
                        out += '<' + chunks[1] + '> '
                        out += escape(child.text)
                    elif isinstance(child, PlotCells):
                        out += emit_label(child, element.direction)
                    else:
                        raise NotImplementedError(f"did not know how to render {child}")
                out += ' '
            if element.direction != curr_direction:
                out += '}'
            return out
        assert_never(element)

    def emit_toplevel(element: PlotElement) -> None:
        if isinstance(element, PlotNode):
            label = emit_label(element.label)
            nodes.append((nonnull(element.id), label, element.shape, 'transparent'))
        elif isinstance(element, PlotEdge):
            edges.append((nonnull(element.a.id), nonnull(element.b.id), element.label))
        else:
            raise NotImplementedError(f"did not know how to render {element}")

    for child in plotter.children:
        emit_toplevel(child)

    for id, label, shape, color in nodes:
        dot.node(id, label=label, shape=shape)
    for a, b, label in edges:
        dot.edge(a, b, label)

    print(dot.source)

    dot.render(view=view, format=format)

if __name__ == '__main__':
    class Matrix(Record):
        elements: list[list[int]]
    visualize(Matrix([ [1, 2, 3], [4, 5 ,6] ]))

