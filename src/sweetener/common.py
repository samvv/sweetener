
from typing import Any, Callable, TypeGuard

type PathElement = str | int

type Path = list[PathElement]

type PathLike = Path | str

def parse_path(path: str) -> Path:
    elements = []
    for chunk in path.split('.'):
        try:
            element = int(chunk)
        except ValueError:
            element = chunk
        elements.append(element)
    return elements

def get(value: Any, path: PathLike):
    if isinstance(path, str):
        path = parse_path(path)
    for chunk in path:
        if isinstance(value, tuple) or isinstance(value, list):
            assert(isinstance(chunk, int))
            value = value[chunk]
        elif isinstance(value, object):
            assert(isinstance(chunk, str))
            value = getattr(value, chunk)
        elif isinstance(value, dict):
            value = value[chunk]
        else:
            raise NotImplementedError(f"did not know how to get {chunk} from {value}")
    return value

def lift(proc: Callable[..., Any], key: PathLike) -> Callable[..., Any]:
    if isinstance(key, str):
        key = parse_path(key)
    def lifted(*args):
        return proc(*(get(arg, key) for arg in args))
    return lifted

def swap(a, i, j):
  a[i], a[j] = a[j], a[i]

