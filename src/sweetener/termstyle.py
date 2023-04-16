
import sys
import os

try:
    import curses
except ImportError:
    curses = None

_COLORS = [
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white',
]

_FORE_COLORS = {
    'black'   : '\u001b[30m',
    'red'     : '\u001b[31m',
    'green'   : '\u001b[32m',
    'yellow'  : '\u001b[33m',
    'blue'    : '\u001b[34m',
    'magenta' : '\u001b[35m',
    'cyan'    : '\u001b[36m',
    'white'   : '\u001b[37m',
}

_FORE_COLORS_BRIGHT = {
    'black'   : '\u001b[30;1m',
    'red'     : '\u001b[31;1m',
    'green'   : '\u001b[32;1m',
    'yellow'  : '\u001b[33;1m',
    'blue'    : '\u001b[34;1m',
    'magenta' : '\u001b[35;1m',
    'cyan'    : '\u001b[36;1m',
    'white'   : '\u001b[37;1m',
}

_BACK_COLORS = {
    'black'   : '\u001b[40m',
    'red'     : '\u001b[41m',
    'green'   : '\u001b[42m',
    'yellow'  : '\u001b[43m',
    'blue'    : '\u001b[44m',
    'magenta' : '\u001b[45m',
    'cyan'    : '\u001b[46m',
    'white'   : '\u001b[47m',
}

_BACK_COLORS_BRIGHT = {
    'black'   : '\u001b[40;1m',
    'red'     : '\u001b[41;1m',
    'green'   : '\u001b[42;1m',
    'yellow'  : '\u001b[43;1m',
    'blue'    : '\u001b[44;1m',
    'magenta' : '\u001b[45;1m',
    'cyan'    : '\u001b[46;1m',
    'white'   : '\u001b[47;1m',
}

class TerminalStyles:

    FG_BLACK: str = ''
    FG_RED: str = ''
    FG_GREEN: str = ''
    FG_YELLOW: str = ''
    FG_BLUE: str = ''
    FG_MAGENTA: str = ''
    FG_CYAN: str = ''
    FG_WHITE: str = ''

    BG_BLACK: str = ''
    BG_RED: str = ''
    BG_GREEN: str = ''
    BG_YELLOW: str = ''
    BG_BLUE: str = ''
    BG_MAGENTA: str = ''
    BG_CYAN: str = ''
    BG_WHITE: str = ''

    FG_BRIGHTBLACK: str = ''
    FG_BRIGHTRED: str = ''
    FG_BRIGHTGREEN: str = ''
    FG_BRIGHTYELLOW: str = ''
    FG_BRIGHTBLUE: str = ''
    FG_BRIGHTMAGENTA: str = ''
    FG_BRIGHTCYAN: str = ''
    FG_BRIGHTWHITE: str = ''

    BG_BRIGHTBLACK: str = ''
    BG_BRIGHTRED: str = ''
    BG_BRIGHTGREEN: str = ''
    BG_BRIGHTYELLOW: str = ''
    BG_BRIGHTBLUE: str = ''
    BG_BRIGHTMAGENTA: str = ''
    BG_BRIGHTCYAN: str = ''
    BG_BRIGHTWHITE: str = ''

    RESET: str = ''
    BOLD: str = ''
    ITALIC: str = ''

    def __init__(self, enable=None):

        if enable is None:
            enable = os.isatty(2)

        if not enable:
            return

        if curses is not None:
            curses.setupterm()
            max_colors = curses.tigetnum('colors')
            if max_colors >= 16:
                enable_bright = True

        setattr(self, 'BOLD', '\u001b[1')
        setattr(self, 'ITALIC', '\u001b[3')
        setattr(self, 'RESET', '\u001b[32m')

        # TODO

termstyle = TerminalStyles()
