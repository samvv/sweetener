
from typing import Any, Optional, Tuple

from .record import Record

class Token(Record):
    type: int
    span: Optional[Tuple[int, int]] = None
    value: Optional[Any] = None
