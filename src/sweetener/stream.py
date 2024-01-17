
from collections import deque
from typing import Callable, Generic, Protocol, TypeVar

T = TypeVar('T', covariant=True)

class Stream(Generic[T], Protocol):

    def peek(self, lookahead: int) -> T: ...

    def get(self) -> T: ...

class BufferStream(Stream[T]):

    def __init__(self, generator: Callable[[], T]):
        self.generator = generator
        self.buffer = deque()

    def peek(self, lookahead: int = 1) -> T:
        while lookahead < len(self.buffer):
            element = self.generator()
            self.buffer.append(element)
        return self.buffer[lookahead-1]

    def get(self) -> T:
        return self.buffer.popleft() if self.buffer else self.generator()

class VectorStream(Stream[T]):

    def __init__(self, data, sentry, offset=0):
        self.data = data
        self.sentry = sentry
        self.offset = offset

    def peek(self, lookahead: int = 1) -> T:
        offset = self.offset + lookahead - 1
        if offset < len(self.data):
            return self.data[offset]
        return self.sentry

    def get(self):
        if self.offset >= len(self.data):
            return self.sentry
        element = self.data[self.offset]
        self.offset += 1
        return element

