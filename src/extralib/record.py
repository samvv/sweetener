
import typing
import json
from inspect import isclass

from .serde import serialize, deserialize, serializable
from .util import HORIZONTAL, VERTICAL
from .ops import clone, equal

def is_list_type(ty):
    return hasattr(ty, '__origin__') and ty.__origin__ == list

def is_union_type(ty):
    return hasattr(ty, '__origin__') and ty.__origin__ == typing.Union

def is_none_type(ty):
    return ty == type(None)

def flatten_union_type(ty):
    if is_union_type(ty):
        return ((el2_ty for el_ty in ty.__args__ for el2_ty in flatten_union_type(el_ty)))
    else:
        return [ty]

def is_type_optional(ty):
    return any(is_none_type(el_ty) for el_ty in flatten_union_type(ty))

def get_element_type(ty):
    if is_list_type(ty):
        return ty.__args__[0]
    elif is_union_type(ty):
        return next(get_element_type(el_ty) for el_ty in flatten_union_type(ty) if not is_none_type(el_ty))
    else:
        return ty

def is_tuple_type(ty):
    return hasattr(ty, '__origin__') and ty.__origin__ == tuple

def is_special_type(ty):
    return ty == typing.Any or is_none_type(ty)

def get_index_type(ty):
    if is_list_type(ty):
        return int
    else:
        return None

def satisfies_type(val, ty):
    if isclass(ty):
        return isinstance(val, ty)
    elif ty == typing.Any:
        return True
    elif is_none_type(ty):
        return val is None
    elif is_list_type(ty):
        return isinstance(val, list) and all(satisfies_type(el, ty.__args__[0]) for el in val)
    elif is_union_type(ty):
        return any(satisfies_type(val, arg) for arg in ty.__args__)
    elif is_tuple_type(ty):
        return isinstance(val, tuple) and all(satisfies_type(el, type_arg) for el, type_arg in zip(val, ty.__args__))
    raise NotImplementedError(f"type checking for the {ty} is not implemented")

# def get_all_annotations(cls):
#     annotations = dict()
#     prev_annotations = None
#     for cls in reversed(cls.__mro__):
#         if hasattr(cls, '__annotations__') and cls.__annotations__ != prev_annotations:
#             prev_annotations = cls.__annotations__
#             for name, ty in cls.__annotations__.items():
#                 yield SimpleNamspace(name, ty, name in cls.__dict__, cls.__dict__.get(name))

def has_annotation(cls, expected):
    prev_annotations = None
    for cls in cls.__mro__:
        if hasattr(cls, '__annotations__') and cls.__annotations__ != prev_annotations:
            if expected in cls.__annotations__:
                return True
            else:
                prev_annotations = cls.__annotations__
    return False

def get_all_subclasses(cls):
    yield cls
    for subcls in cls.__subclasses__():
        yield from get_all_subclasses(subcls)

def find_subclass_named(name, cls):
    for subcls in get_all_subclasses(cls):
        if subcls.__name__ == name:
            return subcls
    raise NameError(f"class named '{name}' not found")

@serializable
class Record:

    def __init__(self, *args, **kwargs):

        fields = self.__dict__['fields'] = dict()
        type_hints = typing.get_type_hints(self.__class__)
        defaults = dict((name, self.__class__.__dict__[name]) for name, ty in type_hints.items() if name in self.__class__.__dict__)
        i = 0

        for name, ty in type_hints.items():
            if name in defaults:
                continue
            if name in kwargs:
                value = kwargs[name]
                del kwargs[name]
            elif i < len(args):
                value = args[i]
                i += 1
            else:
                raise TypeError(f"argument '{name}' is required but did not receive a value")
            if not satisfies_type(value, ty):
                raise TypeError(f"{value} did not satisfy type {ty}")
            fields[name] = value

        for name, default in defaults.items():
            ty = type_hints[name]
            if name in kwargs:
                value = kwargs[name]
                del kwargs[name]
            elif i < len(args):
                value = args[i]
                i += 1
            else:
                value = default
            if not satisfies_type(value, ty):
                raise TypeError(f"{value} did not satisfy type {ty}")
            fields[name] = value

        if i < len(args) or len(kwargs) > 0:
            # missing = list()
            # for name in type_hints:
            #     if name not in fields:
            #         missing.append(name)
            # for name in defaults:
            #     if name not in fields:
            #         missing.append(name)
            # raise TypeError("missing arguments: {pretty_enum(")
            raise TypeError("excess arguments received: {len(args)} positional, {pretty_enum(kwargs.keys())}")

    def get_field_names(self):
        return self.fields.keys()

    def items(self):
        return self.fields.items()

    def __getitem__(self, key):
        return self.fields[key]

    def __setitem__(self, key, value):
        self.fields[key] = value

    def resolve(self, key):
        return self.fields[key]

    def expand(self):
        return self.fields.items()
        # for k, v in self.fields.items():
        #     if isinstance(v, list):
        #         for el in v:
        #             if isinstance(el, Record):
        #                 yield k, el
        #     elif isinstance(v, Record):
        #         yield v

    def clone(self, deep=False):
        kwargs = self.fields if not deep else dict((k, clone(v, deep=True)) for k, v in self.fields.items())
        return self.__class__(**kwargs)

    def __getattribute__(self, name):
        if name.startswith('__') or name == 'fields':
            return super().__getattribute__(name)
        elif name in self.fields:
            return self.fields[name]
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name.startswith('__') or name == 'fields':
            super().__setattr__(name, value)
        elif name in self.fields:
            self.fields[name] = value
        else:
            self.__dict__[name] = value

    def serialize(self):
        return dict((k, serialize(v)) for k, v in self.fields.items())

    def deserialize(value, cls):
        kwargs = dict((k, deserialize(v)) for k, v in value.items())
        return cls(**kwargs)

    def equal(a, b):
        if type(a) != type(b):
            return False
        for name, _ty in typing.get_type_hints(a).items():
            if not equal(getattr(a, name), getattr(b, name)):
                return False
        return True

    def plot(self, plot):
        node = plot.add_node(label=self.__class__.__name__, shape='record', direction=VERTICAL)
        for (key, value) in self.fields.items():
            p = plot(value, key=key)
            if p.is_embeddable:
                row = node.label.add_cells(direction=HORIZONTAL, key=f'field-{key}')
                row.add_text(key)
                row.add_element(p)
            else:
                plot.add_edge(node, p, label=key)
        return node

