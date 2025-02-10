
from functools import cmp_to_key
import types
import typing
from typing import Any, Callable, Generator, TypeAliasType, TypeVar, cast

from sweetener.logging import warn
from sweetener.ops import lift_key
from sweetener.util import make_comparator, primitive_types

_T = TypeVar('_T')

type CoerceFn[_T] = Callable[[Any, type[_T]], _T]

_class_coercions = list[tuple[type, CoerceFn]]()

def add_coercion(cls: type, proc: CoerceFn) -> None:
    assert(cls not in _class_coercions)
    _class_coercions.append((cls, proc))

_Type = TypeVar('_Type', bound=type)

def coercion(cls: type):
    def decorator(func):
        add_coercion(cls, func)
        return func
    return decorator

@coercion(list)
def _coerce_to_list(value, ty) -> list:
    if value is None: return []
    args = typing.get_args(ty)
    return list(coerce(element, args[0]) for element in value)

@coercion(tuple)
def _coerce_to_tuple(value, ty) -> tuple:
    el_tys = typing.get_args(ty)
    return tuple(coerce(element, el_ty) for element, el_ty in zip(value, el_tys))

@coercion(dict)
def _coerce_to_dict(value, ty) -> dict:
    args = typing.get_args(ty)
    out = {}
    for k, v in value.items():
        k_2 = coerce(k, args[0])
        v_2 = coerce(v, args[1])
        out[k_2] = v_2
    return out

@coercion(float)
def _coerce_to_float(value, ty) -> float:
    return float(value)

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
    has_non_type = False
    types = []

    for ty in _get_all_types(ty):
        origin = typing.get_origin(ty)
        if ty in primitive_types and isinstance(value, ty):
            # Fast path for primitive types
            return cast(_T, value)
        if ty is type(None):
            has_none = True
        elif origin is None:
            types.append(ty)
        elif origin is not None:
            types.append(origin)
        else:
            has_non_type = True

    if has_non_type:
        raise CoercionError(f'could not coerce {value} to {ty} because {arg} contains unrecognised types') # type: ignore

    if not types:
        raise CoercionError(f'could not coerce {value} to {ty} because there are no classes to coerce to')

    attempts = list[tuple[Any, CoerceFn]]()
    remaining = list[Any]()

    # Scan all registered coercion functions for matching types
    for cls in types:
        match = False
        for cls_2, proc in _class_coercions:
            if cls is cls_2 or issubclass(cls, cls_2):
                attempts.append((cls, proc))
                match = True
        if not match:
            remaining.append(cls)

    # Whatever classes that failed to match may have a superclass in common
    # We scan the registered coercion functions again but now with this superclass
    if remaining:
        cls = _get_common_superclass(remaining)
        if cls is not None:
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

