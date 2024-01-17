
import json
from pathlib import Path
import pytest
import io

from .text import LineIndex, write_excerpt

def test_line_index_empty():
    idx = LineIndex('')
    assert(idx.count_lines() == 1)

def test_line_index_get_line():
    idx = LineIndex('foo\nbar\nbax\n')
    assert(idx.count_lines() == 4)
    assert(idx.get_line(0) == 1)
    assert(idx.get_line(1) == 1)
    assert(idx.get_line(2) == 1)
    assert(idx.get_line(3) == 1)
    assert(idx.get_line(4) == 2)
    assert(idx.get_line(5) == 2)
    assert(idx.get_line(6) == 2)
    assert(idx.get_line(7) == 2)
    assert(idx.get_line(8) == 3)
    assert(idx.get_line(9) == 3)
    assert(idx.get_line(10) == 3)
    assert(idx.get_line(11) == 3)
    with pytest.raises(RuntimeError):
        idx.get_line(12)

def test_line_index_get_column():
    idx = LineIndex('foo\nbar\nbax\n')
    assert(idx.count_lines() == 4)
    assert(idx.get_column(0) == 1)
    assert(idx.get_column(1) == 2)
    assert(idx.get_column(2) == 3)
    assert(idx.get_column(3) == 4)
    assert(idx.get_column(4) == 1)
    assert(idx.get_column(5) == 2)
    assert(idx.get_column(6) == 3)
    assert(idx.get_column(7) == 4)
    assert(idx.get_column(8) == 1)
    assert(idx.get_column(9) == 2)
    assert(idx.get_column(10) == 3)
    assert(idx.get_column(11) == 4)
    with pytest.raises(RuntimeError):
        idx.get_column(12)

def test_line_index_get_offset():
    idx = LineIndex('foo\nbar\nbax\n')
    assert(idx.count_lines() == 4)
    assert(idx.get_offset(1) == 0)
    assert(idx.get_offset(2) == 4)
    assert(idx.get_offset(3) == 8)
    assert(idx.get_offset(4) == 12)

def test_line_index_get_offset_eof_no_newline():
    idx = LineIndex('foo\nbar\nbax\nbaa')
    assert(idx.count_lines() == 4)
    assert(idx.get_offset(5) == 15)
    with pytest.raises(RuntimeError):
        idx.get_offset(6)

def test_line_index_get_offset_eof_newline():
    idx = LineIndex('foo\nbar\nbax\n')
    assert(idx.count_lines() == 4)
    assert(idx.get_offset(5) == 12)
    with pytest.raises(RuntimeError):
        idx.get_offset(6)

test_cache_dir = Path(__file__).parent.parent.parent / 'test-cache'

def read_file(file: Path, encoding = 'utf-8') -> str:
    with open(file, 'r', encoding=encoding) as f:
        return f.read()

def test_except_foobar():
    for file in test_cache_dir.iterdir():
        if not file.is_file():
            continue
        text = read_file(file)
        i1 = text.index('---\n')
        i2 = text.index('---\n', i1 + 4)
        obj = json.loads(text[i1+4:i2])
        start = obj[0]
        end = obj[1]
        expected = text[i2+4:]
        out = io.StringIO()
        write_excerpt(out, text, (start, end))
        actual = out.getvalue()
        if expected:
            assert(actual == expected)
        else:
            with open(file, 'a') as f:
                f.write(actual);
            raise RuntimeError(f"Test '{file.stem}' had no expected value. The current output has been saved as the expected output. Re-run pytest to let the tests pass.")
