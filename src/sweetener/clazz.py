
def hasmethod(value, name):
    return hasattr(value, name) \
        and callable(getattr(value, name))

