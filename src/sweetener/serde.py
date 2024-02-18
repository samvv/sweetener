
from typing import Any, Protocol, TypeGuard

TYPE_NONE   = 0
TYPE_INT    = 1
TYPE_BOOL   = 2
TYPE_STRING = 3
TYPE_FLOAT  = 4
TYPE_LIST   = 5
TYPE_DICT   = 6
TYPE_CLASS  = 7
TYPE_TUPLE  = 8

type Serializable = None | bool | int | float | str | tuple[Serializable, ...] | list[Serializable] | dict[Serializable, Serializable]

type Data = None | bool | int | float | str | list[Data] | dict[Data, Data]

class SerializableObject(Protocol):
    def serialize(self) -> Data: ...

def is_serializable_object(value: Any) -> TypeGuard[SerializableObject]:
    return isinstance(value, object) \
        and hasattr(value, 'serialize') \
        and callable(getattr(value, 'serialize'))

def serialize(value: Serializable) -> Data:
    if value is None:
        return [TYPE_NONE]
    elif isinstance(value, int):
        return [TYPE_INT, value]
    elif isinstance(value, float):
        return [TYPE_FLOAT, value]
    elif isinstance(value, bool):
        return [TYPE_BOOL, value]
    elif isinstance(value, str):
        return [TYPE_STRING, value]
    elif isinstance(value, list):
        return [TYPE_LIST, list(serialize(el) for el in value)]
    elif isinstance(value, tuple):
        return [TYPE_TUPLE, list(serialize(el) for el in value)]
    elif isinstance(value, dict):
        return [TYPE_DICT, dict((serialize(k), serialize(v)) for (k, v) in value.items())]
    elif is_serializable_object(value):
        return [TYPE_CLASS, value.__class__.__name__, value.serialize()]
    else:
        raise NotImplementedError(f"did not know how to serialize {value}")

serializable_classes = dict()

def serializable(cls):
    serializable_classes[cls.__name__] = cls
    return cls

def deserialize(data: Data) -> Serializable:
    assert(isinstance(data, list))
    if data[0] == TYPE_NONE:
        return None
    elif data[0] == TYPE_INT:
        assert(isinstance(data[1], int))
        return data[1]
    elif data[0] == TYPE_BOOL:
        assert(isinstance(data[1], bool))
        return data[1]
    elif data[0] == TYPE_FLOAT:
        assert(isinstance(data[1], float))
        return data[1]
    elif data[0] == TYPE_STRING:
        assert(isinstance(data[1], str))
        return data[1]
    elif data[0] == TYPE_LIST:
        assert(isinstance(data[1], list))
        return list(deserialize(el) for el in data[1])
    elif data[0] == TYPE_TUPLE:
        assert(isinstance(data[1], list))
        return tuple(deserialize(el) for el in data[1])
    elif data[0] == TYPE_DICT:
        assert(isinstance(data[1], dict))
        return dict((deserialize(k), deserialize(v)) for k, v in data[1].items())
    elif data[0] == TYPE_CLASS:
        cls = serializable_classes[data[1]]
        return cls.deserialize(data[2], cls)
    else:
        raise NotImplementedError(f"unknown serialization type {data[0]}")

