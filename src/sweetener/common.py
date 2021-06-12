
def get(value, path):
    if isinstance(path, str):
        path = path.split('.')
    if not isinstance(path, list):
        path = [path]
    for chunk in path:
        if isinstance(value, tuple) or isinstance(value, list):
            value = value[int(chunk)]
        elif isinstance(value, object):
            value = getattr(value, chunk)
        elif isinstance(value, dict):
            value = value[chunk]
        else:
            raise NotImplementedError(f"did not know how to get {chunk} from {value}")
    return value

def lift(proc, key):
    def lifted(*args):
        return proc(*(get(arg, key) for arg in args))
    return lifted

def swap(a, i, j):
  a[i], a[j] = a[j], a[i]

def ischar(value):
    return isinstance(value, str) \
        and len(value) == 1

def isprimitive(value):
    return value is None \
        or isinstance(value, str) \
        or isinstance(value, bool) \
        or isinstance(value, float) \
        or isinstance(value, int)

