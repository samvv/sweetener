
import re
import io
from typing import TextIO
from colorama import Fore, Back, Style

from .ansicodes import *
from .colors import *
from .math import count_digits

_re_whitespace = re.compile('[\n\r\t ]')

class IndentWriter:

    def __init__(self, out: io.TextIOBase | None = None, indentation='  '):
        if out is None:
            out = io.StringIO()
        self.output = out
        self.at_blank_line = True
        self.newline_count = 0
        self.indent_level = 0
        self.indentation = indentation
        self._re_whitespace = re.compile('[\n\r\t ]')

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def ensure_trailing_lines(self, count):
        self.write('\n' * max(0, count - self.newline_count))

    def write(self, text: str) -> None:
        for ch in text:
            if ch == '\n':
                self.newline_count = self.newline_count + 1 if self.at_blank_line else 1
                self.at_blank_line = True
            elif self.at_blank_line and not self._re_whitespace.match(ch):
                self.newline_count = 0
                self.output.write(self.indentation * self.indent_level)
                self.at_blank_line = False
            self.output.write(ch)

EOF = '\uFFFF'

class LineIndex:

    def __init__(self, text: str):
        self.text = text
        self.lines = list()

    def __iter__(self):
        return iter(self.text)

    def __getitem__(self, key):
        return self.text[key]

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text

    def _count_lines_until_offset(self, end_offset):
        end_offset = min(end_offset, len(self.text)-1)
        line = 1 if not self.lines else len(self.lines)+1
        offset = 0 if line == 1 else self.lines[line-2]
        while offset <= end_offset:
            ch = self.text[offset]
            offset += 1
            if ch == '\n':
                self.lines.append(offset)
                line += 1

    def _count_lines_until_line(self, end_line):
        max_length = len(self.text)
        line = 1 if not self.lines else len(self.lines)+1
        offset = 0 if line == 1 else self.lines[line-2]
        while line <= end_line:
            if offset >= max_length:
                if offset == max_length:
                    return line+1
                raise RuntimeError(f'line index out of bounds')
            ch = self.text[offset]
            offset += 1
            if ch == '\n':
                self.lines.append(offset)
                line += 1
                if line == end_line:
                    break

    def get_offset(self, line):
        if line < 1:
            raise RuntimeError(f'line index out of bounds')
        if line == 1:
            return 0
        self._count_lines_until_line(line)
        if line-2 >= len(self.lines):
            if line-2 == len(self.lines):
                return len(self.text)
            raise RuntimeError(f'line index out of bounds')
        return self.lines[line-2]

    def get_column(self, offset):
        return offset - self.get_offset(self.get_line(offset)) + 1

    def get_line(self, offset):
        if offset == 0:
            return 1
        if offset >= len(self.text):
            raise RuntimeError(f'offset out of text bounds')
        self._count_lines_until_offset(offset)
        for i, line_start_offset in enumerate(self.lines):
            if line_start_offset > offset:
                return i+1
        return len(self.lines)+1

    def count_lines(self):
        self._count_lines_until_offset(len(self.text)-1)
        return len(self.lines)+1

class TextFile:

    def __init__(self, text='', name: str | None = None):
        self.text = text
        self.name = name
        self._line_index = LineIndex(text)

    def get_line_offset(self, line):
        return self._line_index.get_offset(line)

    def get_column(self, offset):
        return self._line_index.get_column(offset)

    def get_line(self, offset):
        return self._line_index.get_line(offset)

    def count_lines(self):
        return self._line_index.count_lines()

    def __getitem__(self, index):
        return self.text[index]

def write_excerpt(
    out: TextIO,
    text: TextFile | str,
    span: tuple[int, int],
    lines_pre=1,
    lines_post=1,
    gutter_width: int | None = None,
    message: str | None = None,
    line_color: Color = WHITE,
):

    if not isinstance(text, TextFile):
        text = TextFile(text)

    start_line = text.get_line(span[0])
    end_line = text.get_line(span[1])
    start_line_offset = text.get_line_offset(start_line)
    end_line_offset = text.get_line_offset(end_line+1)
    start_column = span[0] - start_line_offset + 1
    end_column = span[1] - text.get_line_offset(end_line) + 1
    pre_line = max(start_line-lines_pre, 1)
    pre_offset = text.get_line_offset(pre_line)
    post_offset = text.get_line_offset(end_line+lines_post+1)

    if gutter_width is None:
        gutter_width = max(2, count_digits(end_line+lines_post))

    # initial position in text
    at_blank_line = True
    line = pre_line
    column = 1

    def write(ch):
        nonlocal line, column, at_blank_line
        if at_blank_line:
            print_gutter(line)
        if ch == '\n':
            line += 1
            at_blank_line = True
        elif not _re_whitespace.match(ch):
            at_blank_line = False

    def print_guttered(start, end):
        nonlocal out, line, at_blank_line
        for i in range(start, end):
            write(text[i])

    def print_gutter(line=None):
        nonlocal out
        num_width = 0 if line is None else count_digits(line)
        out.write(Fore.BLACK + Back.WHITE)
        for i in range(0, gutter_width - num_width):
            out.write(' ')
        if line is not None:
            out.write(str(line))
        out.write(Style.RESET_ALL + ' ')

    def print_underline():
        nonlocal out
        k = start_column if line == start_line else 1
        l = end_column if line == end_line else column
        should_print_message = line == end_line and message is not None
        if l > k:
            out.write('\n')
            print_gutter()
            for _ in range(0, k-1):
                out.write(' ')
            out.write(Fore.RED)
            for _ in range(k-1, l-1):
                out.write('~')
            out.write(Style.RESET_ALL)

    print_gutter(line)

    print_guttered(pre_offset, start_line_offset)

    for i in range(start_line_offset, end_line_offset):
        ch = text[i]
        if ch == '\n':
            print_underline()
            line += 1
            column = 1
            out.write('\n')
            print_gutter(line)
        else:
            column += 1
            out.write(ch)

    print_guttered(end_line_offset, post_offset)

    out.write('\n')

    return out

