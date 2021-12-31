
import functools

class Tracer:

    def __init__(self, out=None) -> None:
        if out is None:
            out = sys.stderr
        self.out = IndentWriter(out)
        self._stack = []

    def trace(self, name: str, *args, **kwargs):
        self.out.write(f'{ANSI_GREEN}{name}{ANSI_RESET}')
        for arg in args:
            self.out.write(f' {arg}')
        for k, v in kwargs.items():
            self.out.write(f' {ANSI_YELLOW}{k}{ANSI_RESET}={v}')
        self.out.write('\n')

    def _start_call(self, name: str, args, kwargs):
        self.out.write(f'{ANSI_BOLD}{ANSI_YELLOW}start{ANSI_RESET} {ANSI_GREEN}{name}{ANSI_RESET}')
        for arg in args:
            self.out.write(f' {arg}')
        for k, v in kwargs.items():
            self.out.write(f' {ANSI_YELLOW}{k}{ANSI_RESET}={v}')
        self.out.write('\n')
        self.out.indent()
        ns = time.perf_counter()
        self._stack.append((name, ns))

    def _end_call(self, name: str, *args, **kwargs):
        name_2, ns = self._stack.pop()
        diff = time.perf_counter() - ns
        self.out.dedent()
        self.out.write(f'{ANSI_BOLD}{ANSI_YELLOW}end{ANSI_RESET} {name_2} [elapsed {ANSI_BLUE}{diff:.5f}ns{ANSI_RESET}]\n')

_global_tracer = Tracer()

def trace(name: str, *args, **kwargs):
    _global_tracer.trace(name, *args, **kwargs)

def traced(proc):
    @functools.wraps(proc)
    def wrapper(*args, **kwargs):
        _global_tracer._start_call(proc.__name__, args, kwargs)
        out = proc(*args, **kwargs)
        _global_tracer._end_call(proc.__name__)
        return out
    return wrapper

