
import typing
import inspect
from typing import Any, Iterable, Self, TypeVar, cast

from sweetener.typing import CoercionError, add_coercion, coerce, satisfies_type

from .ops import clone
from .util import get_class_name, get_type_index, pretty_enumerate, reflect, primitive_types

_T = TypeVar('_T')

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

# def has_annotation(cls: type, expected: str) -> bool:
#     prev_annotations = None
#     for cls in cls.__mro__:
#         if hasattr(cls, '__annotations__') and cls.__annotations__ != prev_annotations:
#             if expected in cls.__annotations__:
#                 return True
#             else:
#                 prev_annotations = cls.__annotations__
#     return False

# def get_all_subclasses(cls: type) -> Generator[type, None, None]:
#     yield cls
#     for subcls in cls.__subclasses__():
#         yield from get_all_subclasses(subcls)

# def find_subclass_named(name: str, cls: type) -> type:
#     for subcls in get_all_subclasses(cls):
#         if subcls.__name__ == name:
#             return subcls
#     raise NameError(f"class named '{name}' not found")

def get_defaults(cls: type) -> dict[str, Any]:
    result = dict()
    for pcls in inspect.getmro(cls):
        for k, v in pcls.__dict__.items():
            if k not in result and not k.startswith('__'):
                result[k] = v
    return result

class RecordFields:

    def __init__(self, record) -> None:
        self.record = record

    def __contains__(self, key: str) -> bool:
        hints = typing.get_type_hints(type(self.record))
        return key in hints

    def __getitem__(self, key: str) -> Any:
        hints = typing.get_type_hints(type(self.record))
        if key not in hints:
            raise KeyError(f"key '{key}' is not found in the fields of {self.record}")
        return getattr(self.record, key)

    def __setitem__(self, key: str, new_value: typing.Any) -> None:
        hints = typing.get_type_hints(type(self.record))
        if key not in hints:
            raise KeyError(f"key '{key}' is not found in the fields of {self.record}")
        setattr(self.record, key, new_value)

    def keys(self) -> Iterable[str]:
        hints = typing.get_type_hints(type(self.record))
        return hints.keys()

    def values(self) -> Iterable[Any]:
        for key in typing.get_type_hints(type(self.record)):
            yield getattr(self.record, key)

    def items(self) -> Iterable[tuple[str, Any]]:
        for name in typing.get_type_hints(type(self.record)):
            yield name, getattr(self.record, name)


def transform(value: _T, proc) -> _T:

    new_value = proc(value)
    if new_value != value:
        return new_value

    for cls in primitive_types:
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
        return cast(_T, tuple(new_elements))

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
        return cast(_T, new_elements)

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
        return cast(_T, new_elements)

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
        return cast(_T, new_value)

    raise RuntimeError(f'unexpected {value}')

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
                # We do a clone here so we can e.g. assign an empty list to the
                # default of a field and still be sure that each construction
                # of the record has an unique empty list
                value = clone(defaults[name])
            if not satisfies_type(value, ty):
                raise TypeError(f"{value} did not satisfy type {ty}")
            self.__dict__[name] = value

        if i < len(args) or len(kwargs) > 0:
            parts = []
            if i < len(args):
                parts.append(f'{i-len(args)} positional')
            for k in kwargs:
                parts.append(f"'{k}'")
            raise TypeError(f'excess arguments received to {get_class_name(self)}: {pretty_enumerate(parts)}')

    def get_field_names(self):
        return typing.get_type_hints(self).keys()

    @property
    def fields(self) -> RecordFields:
        return RecordFields(self)

    def items(self):
        return self.fields.items()

    def keys(self):
        return self.fields.keys()

    def _equal(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False
        for k1, v1 in self.fields.items():
            if other[k1] != v1:
                return False
        return True

    def _expand(self) -> Iterable[tuple[str, Any]]:
        return self.fields.items()

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
        import yaml
        print(yaml.dump(self.to_primitive()))

    # FIXME Either use this method or remove it
    def encode(self, encoder) -> None:
        encoder.write_tag(self.__class__.__name__)
        for k, v in self.fields.items():
            encoder.write_field(k, v)

_Record = TypeVar('_Record', bound=Record)

def _coerce_to_record(value: Any, ty: type[_Record]) -> _Record:
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

