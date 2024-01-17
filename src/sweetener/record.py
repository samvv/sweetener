
import yaml
import types
import typing
from functools import cmp_to_key
import collections.abc
import inspect
from typing import Any, Callable, Generator, Protocol, Self, Type, TypeVar, cast

from .logging import warn
from .util import get_class_name, get_type_index, lift_key, reflect, make_comparator

T = TypeVar('T')

_primitive_types = [ type(None), bool, int, float, str ]

def satisfies_type(value: Any, ty: Type) -> bool:

    if ty is None:
        return value is None

    if ty is typing.Any:
        return True

    origin = typing.get_origin(ty)

    if origin is None:
        return isinstance(value, ty)

    args = typing.get_args(ty)

    if origin is typing.Union or origin == types.UnionType:
        return any(satisfies_type(value, arg) for arg in args)

    if origin is dict:
        key_type = args[0]
        value_type = args[1]
        if not isinstance(value, dict):
            return False
        for k, v in value.items():
            if not satisfies_type(k, key_type) or not satisfies_type(v, value_type):
                return False
        return True

    if origin is set:
        element_type = args[0]
        return isinstance(value, set) \
            and all(satisfies_type(v, element_type) for v in value)

    if origin is list:
        element_type = args[0]
        return isinstance(value, list) \
            and all(satisfies_type(v, element_type) for v in value)

    if origin is collections.abc.Callable:
        # TODO check whether the parameter types are satisfied
        return callable(value)

    if origin is tuple:
        if not isinstance(value, tuple) or len(value) != len(args):
            return False
        i = 0
        for element in value:
            element_type = args[i]
            if element_type == Ellipsis:
                element_type = args[i-1]
            else:
                i += 1
            if not satisfies_type(element, element_type):
                return False
        return True

    warn(f'no type-checking logic defined for {origin}')
    return isinstance(value, origin)

def _get_all_union_elements(value: Type):

    origin = typing.get_origin(value)

    if origin is typing.Union:
        args = typing.get_args(value)
        for arg in args:
            yield from _get_all_union_elements(arg)
        return

    yield value

def _lt_helper_dict(a, b):
    keys_a = list(a.keys())
    keys_a.sort()
    keys_b = list(b.keys())
    keys_b.sort()
    i1 = 0
    i2 = 0
    is_equal = True
    while True:
        if i1 == len(keys_a) or i2 == len(keys_b):
            break
        k1 = keys_a[i1]
        k2 = keys_b[i2]
        if _lt_helper(k1, k2):
            is_equal = False
            i1 += 1
        elif is_equal and _lt_helper(k2, k1):
           return False
        else:
            v1 = a[k1]
            v2 = b[k2]
            if _lt_helper(v1, v2):
                is_equal = False
            elif is_equal and _lt_helper(v2, v1):
                return False
            i1 += 1
            i2 += 1
    if is_equal:
        return len(keys_a) < len(keys_b)
    return True

def _lt_helper_sequence(a, b):
    is_equal = True
    for v1, v2 in zip(a, b):
        if _lt_helper(v1, v2):
            is_equal = False
        elif is_equal and _lt_helper(v2, v1):
            return False
    if is_equal:
        return len(a) < len(b)
    return True

def _lt_helper(a, b):
    i1 = get_type_index(a)
    i2 = get_type_index(b)
    if i1 != i2:
        return i1 < i2
    if a is None:
        # b must be None
        return False
    if isinstance(a, dict):
        return _lt_helper_dict(a, b)
    if isinstance(a, list) \
            or isinstance(a, tuple):
        return _lt_helper_sequence(a, b)
    return a < b

def has_annotation(cls: Type, expected: str) -> bool:
    prev_annotations = None
    for cls in cls.__mro__:
        if hasattr(cls, '__annotations__') and cls.__annotations__ != prev_annotations:
            if expected in cls.__annotations__:
                return True
            else:
                prev_annotations = cls.__annotations__
    return False

def get_all_subclasses(cls: Type) -> Generator[Type, None, None]:
    yield cls
    for subcls in cls.__subclasses__():
        yield from get_all_subclasses(subcls)

def find_subclass_named(name: str, cls: Type) -> Type:
    for subcls in get_all_subclasses(cls):
        if subcls.__name__ == name:
            return subcls
    raise NameError(f"class named '{name}' not found")

def get_defaults(cls: Type) -> dict[str, Any]:
    result = dict()
    for pcls in inspect.getmro(cls):
        for k, v in pcls.__dict__.items():
            if k not in result and not k.startswith('__'):
                result[k] = v
    return result

type CoerceFn = Callable[[Any, Type], Type]

_class_coercions = list[tuple[Type, CoerceFn]]()

def add_coercion(cls: Type, proc: CoerceFn) -> None:
    assert(cls not in _class_coercions)
    _class_coercions.append((cls, proc))

class CoercionError(RuntimeError):
    pass

def get_all_superclasses(cls: Type) -> Generator[Type, None, None]:
    yield cls
    for parent_cls in cls.__bases__:
        yield from get_all_superclasses(parent_cls)

def get_common_superclass(classes: list[Type]) -> Type | None:
    cls = classes[0]
    for parent_cls in get_all_superclasses(cls):
        if all(issubclass(cls, parent_cls) for cls in classes):
            return parent_cls

def coerce(value: Any, ty: Type) -> Any:

    if ty is type(None):
        if value is not None:
            raise CoercionError(f'could not coerce {value} to NoneType because the only allowed value is None')
        return None

    origin = typing.get_origin(ty)

    if origin is None:

        if isinstance(value, ty):
            return value

        attempts = []

        for cls, proc in _class_coercions:
            if ty is cls or issubclass(ty, cls):
                attempts.append((cls, proc))

        attempts.sort(key=lift_key(cmp_to_key(make_comparator(issubclass)), 0))

        for cls, proc in attempts:
            try:
                return proc(value, ty)
            except CoercionError:
                pass

        raise CoercionError(f'could not coerce {value} to {ty} because no known coercions exist for {ty}')

    if origin is typing.Union:
        classes = []
        has_none = False
        has_non_cls = False
        for arg in _get_all_union_elements(ty):
            if arg is type(None):
                has_none = True
                continue
            origin = typing.get_origin(arg)
            if origin is not None:
                has_non_cls = True
            classes.append(arg)
        if value is None:
            if not has_none:
                raise CoercionError(f'could not coerce None to {ty} because None is not allowed')
            return None
        if has_non_cls:
            raise CoercionError(f'could not coerce {value} to {ty} because {arg} cannot be joined with the other typing.Union elements')
        cls = get_common_superclass(classes)
        if cls is None:
            raise CoercionError(f'could not coerce {value} to {ty} because {ty} can be multiple unrelated types')
        return coerce(value, cls)

    args = typing.get_args(ty)

    if origin is list:
        if value is None:
            return []
        element_type = args[0]
        return list(coerce(element, element_type) for element in value)

    if origin is tuple:
        if value is None:
            return tuple(coerce(None, element_type) for element_type in args)
        return tuple(coerce(element, element_type) for element, element_type in zip(value, args))

    raise RuntimeError(f'cannot coerce {value} into {ty} because {origin} is an unsupported typing')

class RecordFields:

    def __init__(self, record) -> None:
        self.record = record

    def __contains__(self, key: str):
        hints = typing.get_type_hints(type(self.record))
        return key in hints

    def __getitem__(self, key: str) -> typing.Any:
        hints = typing.get_type_hints(type(self.record))
        if key not in hints:
            raise KeyError(f"key '{key}' is not found in the fields of {self.record}")
        return getattr(self.record, key)

    def __setitem__(self, key: str, new_value: typing.Any):
        hints = typing.get_type_hints(type(self.record))
        if key not in hints:
            raise KeyError(f"key '{key}' is not found in the fields of {self.record}")
        setattr(self.record, key, new_value)

    def keys(self):
        hints = typing.get_type_hints(type(self.record))
        return hints.keys()

    def values(self):
        for key in typing.get_type_hints(type(self.record)):
            yield getattr(self.record, key)

    def items(self):
        for name in typing.get_type_hints(type(self.record)):
            yield name, getattr(self.record, name)

def pretty_enum(elements: typing.List[str]) -> str:
    if not elements:
        return 'nothing'
    if len(elements) == 1:
        return elements[0]
    out = elements[0]
    for element in elements[1:-1]:
        out += f', {element}'
    out += f' and {elements[-1]}'
    return out


def transform(value: T, proc) -> T:

    new_value = proc(value)
    if new_value != value:
        return new_value

    for cls in _primitive_types:
        if isinstance(value, cls):
            return value

    if isinstance(value, tuple):
        new_elements = []
        has_new_element = False
        for element in value:
            new_element = transform(element, proc)
            if new_element != element:
                has_new_element = True
            new_elements.append(new_element)
        if not has_new_element:
            return value
        return cast(T, tuple(new_elements))

    if isinstance(value, list):
        new_elements = []
        has_new_element = False
        for element in value:
            new_element = transform(element, proc)
            if new_element != element:
                has_new_element = True
            new_elements.append(new_element)
        if not has_new_element:
            return value
        return cast(T, new_elements)

    if isinstance(value, set):
        new_elements = set()
        has_new_element = False
        for element in value:
            new_element = transform(element, proc)
            if new_element != element:
                has_new_element = True
            new_elements.add(new_element)
        if not has_new_element:
            return value
        return cast(T, new_elements)

    if isinstance(value, Record):
        cls = value.__class__
        kwargs = dict()
        has_new_v = False
        for k, v in value.fields.items():
            new_v = transform(v, proc)
            if new_v != v:
                has_new_v = True
            kwargs[k] = new_v
        if not has_new_v:
            return value
        return cls(**kwargs)

    if isinstance(value, dict):
        new_value = dict()
        has_new_v = False
        for k, v in value.items():
            new_v = transform(v, proc)
            if new_v != v:
                has_new_v = True
            new_value[k] = new_v
        if not has_new_v:
            return value
        return cast(T, new_value)

    raise RuntimeError(f'unexpected {value}')

class Clonable(Protocol):
    def clone(self) -> Self: ...

def clone(value: T, deep = False) -> T:

    for cls in _primitive_types:
        if isinstance(value, cls):
            return value

    if isinstance(value, object) and hasattr(value, 'clone'):
        return cast(Any, value).clone()

    if isinstance(value, dict):
        return cast(T, dict((k, clone(v, True) if deep else v) for k, v in value.items()))

    if isinstance(value, list):
        return cast(T, list(clone(el, True) if deep else el for el in value))

    if isinstance(value, tuple):
        return cast(T, tuple(clone(el, True) if deep else el for el in value))

    if isinstance(value, set):
        return cast(T, set(clone(el, True) if deep else el for el in value))

    raise RuntimeError(f'could not clone {value} becaue it did not have a .clone() and was not recognised as a primitive type')

def _record_clone_helper(value, deep: bool):
    if isinstance(value, dict):
        return dict((k, _record_clone_helper(v, deep)) for k, v in value.items())
    if isinstance(value, list):
        return list(_record_clone_helper(el, deep) for el in value)
    if isinstance(value, tuple):
        return tuple(_record_clone_helper(el, deep) for el in value)
    if not deep:
        return value
    return clone(value, True)

@reflect
class Record:

    def __init__(self, *args, **kwargs):

        type_hints = typing.get_type_hints(self.__class__)
        defaults = get_defaults(self.__class__)
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
                try:
                    value = coerce(None, ty)
                except CoercionError:
                    raise TypeError(f"argument '{name}' is required but did not receive a value")
            if not satisfies_type(value, ty):
                value = coerce(value, ty)
            self.__dict__[name] = value

        for name, ty in type_hints.items():
            if name not in defaults:
                continue
            ty = type_hints[name]
            if name in kwargs:
                value = kwargs[name]
                del kwargs[name]
            elif i < len(args):
                value = args[i]
                i += 1
            else:
                value = defaults[name]
            if not satisfies_type(value, ty):
                raise TypeError(f"{value} did not satisfy type {ty}")
            self.__dict__[name] = value

        if i < len(args) or len(kwargs) > 0:
            parts = []
            if i < len(args):
                parts.append(f'{i-len(args)} positional')
            for k in kwargs:
                parts.append(f"'{k}'")
            raise TypeError(f'excess arguments received to {get_class_name(self)}: {pretty_enum(parts)}')

    def get_field_names(self):
        return typing.get_type_hints(self).keys()

    @property
    def fields(self):
        return RecordFields(self)

    def items(self):
        return self.fields.items()

    def equal(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False
        for k1, v1 in self.fields.items():
            if other[k1] != v1:
                return False
        return True

    def __lt__(self, other) -> bool:
        if not isinstance(other, Record):
            return _lt_helper(self, other)
        return _lt_helper(self.fields, other.fields)

    def __getitem__(self, name: str):
        return self.fields[name]

    def __setitem__(self, key: str, new_value: Any) -> None:
        self.fields[key] = new_value

    def __setattr__(self, name: str, new_value: Any) -> None:
        hints = typing.get_type_hints(type(self))
        if name in hints:
            ty = hints[name]
            if not satisfies_type(new_value, ty):
                raise RuntimeError(f"cannot set field '{name}' to {new_value} on {get_class_name(self)} because the type {ty} is not satisfied")
        super().__setattr__(name, new_value)

    def clone(self, deep=False) -> Self:
        new_fields = dict()
        for k, v in self.fields.items():
            new_fields[k] = _record_clone_helper(v, deep)
        return self.__class__(**new_fields)

    def to_primitive(self) -> dict[str, Any]:
        fields = { '$type': self.__class__.__name__ }
        def encode(value: Any) -> Any:
            if isinstance(value, tuple):
                return tuple(encode(element) for element in value)
            if isinstance(value, list):
                return list(encode(element) for element in value)
            if isinstance(value, Record):
                return value.to_primitive()
            return value
        for k, v in self.fields.items():
            fields[k] = encode(v)
        return fields

    def dump(self) -> None:
        print(yaml.dump(self.to_primitive()))

    # FIXME Either use this method or remove it
    def encode(self, encoder) -> None:
        encoder.write_tag(self.__class__.__name__)
        for k, v in self.fields.items():
            encoder.write_field(k, v)

def _coerce_to_record(value: Any, ty: Type[T]) -> T:
    hints = typing.get_type_hints(ty)
    defaults = get_defaults(ty)
    required = 0
    for key in hints.keys():
        if key not in defaults:
            required += 1
    if required == 0:
        if value is not None:
            raise CoercionError(f'could not coerce {value} to {ty} because all fields are optional')
        return ty()
    if required == 1:
        return ty(value)
    raise CoercionError(f'could not coerce {value} to {ty} because it requires more than one field')

add_coercion(Record, _coerce_to_record)

