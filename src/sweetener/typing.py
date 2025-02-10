
from functools import cmp_to_key
import types
import typing
from typing import Any, Callable, Generator, TypeAliasType, TypeVar, cast

from sweetener.logging import warn
from sweetener.ops import lift_key
from sweetener.util import make_comparator

_T = TypeVar('_T')

type CoerceFn[_T] = Callable[[Any, type[_T]], _T]

_class_coercions = list[tuple[type, CoerceFn]]()

def add_coercion(cls: type, proc: CoerceFn) -> None:
    assert(cls not in _class_coercions)
    _class_coercions.append((cls, proc))

def _coerce_list(value, ty) -> list:
    if value is None: return []
    args = typing.get_args(ty)
    return list(coerce(element, args[0]) for element in value)

add_coercion(list, _coerce_list)

def _coerce_tuple(value, ty) -> tuple:
    el_tys = typing.get_args(ty)
    return tuple(coerce(element, el_ty) for element, el_ty in zip(value, el_tys))

add_coercion(tuple, _coerce_tuple)

class CoercionError(RuntimeError):
    pass

def _get_all_superclasses(cls: type) -> Generator[type]:
    yield cls
    for parent_cls in cls.__bases__:
        yield from _get_all_superclasses(parent_cls)

def _get_common_superclass(classes: list[type]) -> type | None:
    cls = classes[0]
    for parent_cls in _get_all_superclasses(cls):
        if all(issubclass(cls, parent_cls) for cls in classes):
            return parent_cls

def _get_all_types(ty: Any) -> Generator[Any]:
    if isinstance(ty, TypeAliasType):
        yield from _get_all_types(ty.__value__)
        return
    origin = typing.get_origin(ty)
    if origin is typing.Union or origin is types.UnionType:
        args = typing.get_args(ty)
        for arg in args:
            yield from _get_all_types(arg)
        return
    yield ty

def coerce(value: object, ty: type[_T]) -> _T:

    if not typing.get_origin(ty) and isinstance(value, ty):
        return value

    has_none = False
    has_non_cls = False
    classes = []

    for ty in _get_all_types(ty):
        origin = typing.get_origin(ty)
        if ty is type(None):
            has_none = True
        elif origin is None:
            classes.append(ty)
        elif origin is not None:
            classes.append(origin)
        else:
            has_non_cls = True

    if has_non_cls:
        raise CoercionError(f'could not coerce {value} to {ty} because {arg} contains unrecognised types') # type: ignore

    if not classes:
        raise CoercionError(f'could not coerce {value} to {ty} because there are no classes to coerce to')
    if len(classes) == 1:
        cls = classes[0]
    else:
        cls = _get_common_superclass(classes)
        if cls is None:
            raise CoercionError(f'could not coerce {value} to {ty} because {ty} do not all have any superclasses in common')

    attempts = []

    for cls_2, proc in _class_coercions:
        if cls is cls_2 or issubclass(cls, cls_2):
            attempts.append((cls, proc))

    attempts.sort(key=lift_key(cmp_to_key(make_comparator(issubclass)), 0))

    for cls, proc in attempts:
        try:
            return proc(value, ty)
        except CoercionError:
            pass

    if value is None:
        if not has_none:
            raise CoercionError(f'could not coerce None to {ty} because None is not allowed')
        return cast(_T, None)

    raise CoercionError(f'could not coerce {value} to {ty} because no known coercions exist for {ty}')

def satisfies_type(value: _T, ty: type[_T]) -> bool:

    if ty is None:
        return value is None

    if isinstance(ty, typing.NewType):
        return satisfies_type(value, ty.__supertype__) # type: ignore

    if ty is typing.Any:
        return True

    if isinstance(ty, typing.TypeAliasType):
        return satisfies_type(value, ty.__value__)

    origin = typing.get_origin(ty)

    if origin is None:
        return isinstance(value, ty)

    args = typing.get_args(ty)

    if origin is typing.Union or origin == types.UnionType:
        return any(satisfies_type(value, arg) for arg in args)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        key_type = args[0]
        value_type = args[1]
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

    if origin is Callable:
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

