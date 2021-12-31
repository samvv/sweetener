
def memoise(proc):
    def wrapped(self, *args, **kwargs):
        if not hasattr(self, '__memoised__'):
            self.__memoised__ = dict()
        mapping = self.__memoised__[proc.__name__]
        key = (tuple(args), tuple(kwargs.items()))
        if key in mapping:
            return key
        result = mapping[key] = proc(self, *args, **kwargs)
        return result
    return wrapped

def once(name):
    @property
    def get(self):
        if not hasattr(self, '__memoised__'):
            self.__memoised__ = dict()
        if name in self.__memoised__:
            return self.__memoised__[name]
        method = getattr(self, name)
        result = self.__memoised__[name] = method()
        return result
    return get

