
from pathlib import Path
import graphviz
import os

from .util import is_primitive, has_method, HORIZONTAL, VERTICAL

GRAPHS_DIR = Path('.pygraphs')

def invert_direction(direction):
    if direction == HORIZONTAL:
        return VERTICAL
    elif direction == VERTICAL:
        return HORIZONTAL

class PlotElement:
    def __init__(self, key):
        self.key = key
        self.id = None

class PlotRef(PlotElement):

    is_embeddable = True

    def __init__(self, referenced, key=None):
        super().__init__(key)
        self.referenced = referenced

class PlotResult:
    def __init__(self, data):
        self.reference = None
        self.data = data

class Plot(PlotElement):

    is_embeddable = False

    def __init__(self, referenced, visited, key=None):
        super().__init__(key)
        self.referenced = referenced
        self.visited = visited
        self.children = []

    def add_node(self, *args, **kwargs):
        node = PlotNode(*args, **kwargs)
        self.children.append(node)
        return node

    def add_edge(self, *args, **kwargs):
        edge = PlotEdge(*args, **kwargs)
        self.children.append(edge)
        return edge

    def add_ref(self, *args, **kwargs):
        id = len(self.referenced)
        ref = PlotRef(id, *args, **kwargs)
        self.children.append(ref)
        return ref

    def __call__(self, value, key):
        if is_primitive(value):
            return PlotText(str(value), key=key)
        elif isinstance(value, list):
            table = PlotCells(direction=VERTICAL, key=key)
            for i, child in enumerate(value):
                p = self(child, key=i)
                row = table.add_cells(direction=HORIZONTAL, key=f'{i}-row')
                if p.is_embeddable:
                    row.add_element(p)
                else:
                    text = row.add_text(i, key=f'{i}-ref')
                    self.add_edge(text, p)
            return table
        elif isinstance(value, dict):
            table = PlotCells(direction=VERTICAL, key=key)
            for i, (k, v) in enumerate(value.items()):
                p1 = self(k, f'{i}-key')
                p2 = self(v, f'{i}-value')
                row = table.add_cells(direction=HORIZONTAL, key=f'{i}-row')
                if p1.is_embeddable:
                    row.add_element(p1)
                else:
                    text = row.add_text(i, key=f'{i}-ref')
                    self.add_edge(text, p1)
                if p2.is_embeddable:
                    row.add_element(p2)
                else:
                    text = row.add_text(i, key=f'{i}-ref')
                    self.add_edge(text, p2)
            return table
        elif has_method(value, 'plot'):
            #  if value in self.visited:
            #      result = self.visited[value]
            #      if result.reference is None:
            #          result.reference = self.add_ref(key=key)
            #          self.referenced.append(result.data)
            #      return result.reference
            new_plot = Plot(self.referenced, self.visited, key=key)
            self.children.append(new_plot)
            result = value.plot(new_plot)
            #  self.visited[value] = PlotResult(result)
            return result
        else:
            raise RuntimeError(f"did not know how to plot {value}")

class PlotNode(PlotElement):

    is_embeddable = False

    def __init__(self, label=None, direction=HORIZONTAL, color='transparent', shape='circle', key=None):
        super().__init__(key)
        self._label = PlotCells(direction, key='label')
        if label is not None:
            self._label.add_text(label)
        self.shape = shape

    @property
    def label(self):
        return self._label

class PlotCells(PlotElement):

    is_embeddable = True

    def __init__(self, direction=HORIZONTAL, key=None):
        super().__init__(key)
        self.direction = direction
        self.children = []

    def add_element(self, element):
        self.children.append(element)

    def add_cells(self, *args, **kwargs):
        cells = PlotCells(*args, **kwargs)
        self.children.append(cells)
        return cells

    def add_text(self, *args, **kwargs):
        text = PlotText(*args, **kwargs)
        self.children.append(text)
        return text

class PlotText(PlotElement):

    is_embeddable = True

    def __init__(self, text, key=None):
        super().__init__(key)
        self.text = str(text)

class PlotEdge(PlotElement):

    is_embeddable = False

    def __init__(self, a, b, label=None, key=None):
        super().__init__(key)
        self.a = a
        self.b = b
        self.label = label

def visualize(value, name=None, view=True):

    referenced = []
    visited = dict()
    plot = Plot(referenced, visited, None)
    result = plot(value, None)

    def encode_path(path):
        return '.'.join(str(chunk) for chunk in path)

    def update_cells_ids(element, path, cells_path):

        new_cells_path = list(cells_path)
        if element.key is not None:
            new_cells_path.append(element.key)
        element.id = encode_path(path) + ':' + encode_path(new_cells_path)

        if isinstance(element, Plot):
            for child in element.children:
                update_cells_ids(child, path, new_cells_path)
        elif isinstance(element, PlotCells):
            for child in element.children:
                update_cells_ids(child, path, new_cells_path)
        elif isinstance(element, PlotText):
            pass
        else:
            raise NotImplementedError(f"did not know how to update IDs of {element}")


    def update_ids(element, path, cells_path=[]):

        element.id = encode_path(path)
        new_path = list(path)
        if element.key is not None:
            new_path.append(element.key)

        if isinstance(element, Plot):
            for child in element.children:
                update_ids(child, new_path)
        elif isinstance(element, PlotNode):
            for child in element.label.children:
                update_cells_ids(child, path, [])
        elif isinstance(element, PlotEdge):
           pass 
        elif isinstance(element, PlotRef):
            pass
        else:
            raise NotImplementedError(f"did not know how to update IDs of {element}")

    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    if name is None:
        i = len(list(GRAPHS_DIR.iterdir()))
        filename = GRAPHS_DIR / f"temp{i}.gv"
    else:
        filename = GRAPHS_DIR / f"{name}.gv"

    dot = graphviz.Digraph(filename=filename)

    def render_graph(result, key, dot):

        nodes = []
        edges = []

        def render_cells(cells, curr_direction=HORIZONTAL, is_first=True):
            out = ''
            if cells.direction != curr_direction:
                out += '{'
            for i, element in enumerate(cells.children):
                if i > 0: out += ' | '
                if isinstance(element, PlotText):
                    chunks = element.id.split(':')
                    if len(chunks) == 2:
                        out += ' <' + chunks[1] + '> '
                    out += element.text
                elif isinstance(element, PlotCells):
                    out += render_cells(element, cells.direction, is_first)
                else:
                    raise NotImplementedError(f"did not know how to render {element}")
            if cells.direction != curr_direction:
                out += '}'
            return out

        def render_element(element):
            if isinstance(element, PlotNode):
                label = render_cells(element.label)
                nodes.append((element.id, label, element.shape, 'transparent'))
            elif isinstance(element, PlotEdge):
                edges.append((element.a.id, element.b.id, element.label))
            elif isinstance(element, Plot):
                for child in element.children:
                    render_element(child)
            elif isinstance(element, PlotRef):
                nodes.append((element.id, str(element.referenced), 'diamond', 'pastel251'))
            else:
                raise NotImplementedError(f"did not know how to render {element}")

        render_element(result)

        for id, label, shape, color in nodes:
            dot.node(id, label=label, shape=shape)
        for a, b, label in edges:
            dot.edge(a, b, label)


    update_ids(plot, ['root'])
    for i, reference in enumerate(referenced):
        update_ids(reference, [i])


    render_graph(plot, 'root', dot)
    for i, reference in enumerate(referenced):
        with dot.subgraph(name=f'cluster_{i}') as s:
            s.attr(style='filled', color='lightgrey')
            render_graph(reference, i, dot)

    print(str(dot))
    dot.render(view=view)
