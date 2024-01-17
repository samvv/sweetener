
from pathlib import Path
import sys
import math
import shutil

def write_file(filepath: Path, contents: str):
    with open(filepath, 'w') as file:
        file.write(contents)

def eprint(message):
    print(message, file=sys.stderr)

def mkdirp(filepath):
    Path(filepath).mkdir(parents=True, exist_ok=True)

UNITS = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

def humanbytes(byte_count: int):
    if byte_count == 0:
        return '0B'
    i = math.floor(math.log(byte_count, 1024))
    return f'{(byte_count / pow(1024, i)):.2f}{UNITS[i]}'

def rimraf(filepath: Path):
    if filepath == Path.cwd():
        raise RuntimeError(f'refusing to remove {filepath}: path is the current working directory')
    if filepath == filepath.root:
        raise RuntimeError(f'refusing to remove {filepath}: path points to an entire drive')
    if filepath == Path.home():
        raise RuntimeError(f'refusing to remove {filepath}: path points to a home directory')
    shutil.rmtree(filepath, ignore_errors=True)

