
from inspect import isclass
import json

TYPE_NONE   = 0
TYPE_INT    = 1
TYPE_BOOL   = 2
TYPE_STRING = 3
TYPE_FLOAT  = 4
TYPE_LIST   = 5
TYPE_DICT   = 6
TYPE_CLASS  = 7

def serialize(value):
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
    elif isinstance(value, dict):
        return [TYPE_DICT, dict((serialize(k), serialize(v)) for (k, v) in value.items())]
    elif isinstance(value, object) and hasattr(value, 'serialize') and callable(value.serialize):
        return [TYPE_CLASS, value.__class__.__name__, value.serialize()]
    else:
        raise NotImplementedError(f"did not know how to serialize {value}")

serializable_classes = dict()

def serializable(cls):
    serializable_classes[cls.__name__] = cls
    return cls

def deserialize(data):
    if data[0] == TYPE_NONE:
        return None
    elif data[0] == TYPE_INT:
        return int(data[1])
    elif data[0] == TYPE_BOOL:
        return bool(data[1])
    elif data[0] == TYPE_FLOAT:
        return float(data[1])
    elif data[0] == TYPE_STRING:
        return str(data[1])
    elif data[0] == TYPE_LIST:
        return list(deserialize(el) for el in data[1])
    elif data[0] == TYPE_DICT:
        return dict((deserialize(k), deserialize(v)) for k, v in data[1].items())
    elif data[0] == TYPE_CLASS:
        cls = serializable_classes[data[1]]
        return cls.deserialize(data[2], cls)
    else:
        raise NotImplementedError(f"unknown serialization type {data[0]}")

