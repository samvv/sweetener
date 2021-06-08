
class LineIndex:

    def __init__(self, text):
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

