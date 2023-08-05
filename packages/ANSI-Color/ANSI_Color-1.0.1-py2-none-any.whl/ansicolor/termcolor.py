# -*- coding: utf-8 *-*
 
from __future__ import print_function

import os

__author__ = 'naitiz'


class Fore:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39

    # These are fairly well supported, but not part of the standard.
    LIGHTBLACK_EX = 90
    LIGHTRED_EX = 91
    LIGHTGREEN_EX = 92
    LIGHTYELLOW_EX = 93
    LIGHTBLUE_EX = 94
    LIGHTMAGENTA_EX = 95
    LIGHTCYAN_EX = 96
    LIGHTWHITE_EX = 97


class Back:
    BLACK = 40
    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47
    RESET = 49

    # These are fairly well supported, but not part of the standard.
    LIGHTBLACK_EX = 100
    LIGHTRED_EX = 101
    LIGHTGREEN_EX = 102
    LIGHTYELLOW_EX = 103
    LIGHTBLUE_EX = 104
    LIGHTMAGENTA_EX = 105
    LIGHTCYAN_EX = 106
    LIGHTWHITE_EX = 107


class Style:
    BOLD = 1
    FAINT = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    CONCEALED = 8
    CROSSED = 9
    NORMAL = 22


RESET = '\033[0m'


def colored(text, fg=None, bg=None, st=None):
    """Colorize text.
    See https://en.wikipedia.org/wiki/ANSI_escape_code

    Available text foreground:
        red, green, yellow, blue, magenta, cyan, white.

    Available text background:
        red, green, yellow, blue, magenta, cyan, white.

    Available style:
        bold, dark, underline, blink, reverse, concealed.

        Terminal properties:

        Terminal	bold	dark	underline	blink	reverse	concealed

        xterm	yes	no	yes	bold	yes	yes

        linux	yes	yes	bold	yes	yes	no

        rxvt	yes	no	yes	bold/black	yes	no

        dtterm	yes	yes	yes	reverse	yes	yes

        teraterm	reverse	no	yes	rev/red	yes	no

        aixterm	normal	no	yes	no	yes	yes

        PuTTY	color	no	yes	no	yes	no

        Windows	no	no	no	no	yes	no

        Cygwin SSH	yes	no	color	color	color	yes

        Mac Terminal	yes	no	yes	yes	yes	yes


    Example:
        colored('Hello, World!', 'red', 'grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'
        if fg is not None:
            text = fmt_str % (fg, text)

        if bg is not None:
            text = fmt_str % (bg, text)

        if st is not None:
            from collections import Iterable
            if isinstance(st, Iterable):
                for s in st:
                    text = fmt_str % (s, text)
            else:
                text = fmt_str % (st, text)

        text += RESET
    return text


def cprint(text, fg=None, bg=None, st=None, **kwargs):
    """Print colorize text.

    It accepts arguments of print function.
    """

    print((colored(text, fg, bg, st)), **kwargs)
    pass


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in dir(Style):
        if not str(style).startswith('_'):
            for fg in dir(Fore):
                if not str(fg).startswith('_'):
                    s1 = ''
                    for bg in dir(Back):
                        if not str(bg).startswith('_'):
                            format = ';'.join(
                                [str(getattr(Style, style)), str(getattr(Fore, fg)), str(getattr(Back, bg))])
                            s1 += '\033[%sm %s \033[0m' % (format, format)
                    print(s1)
            print('\n')


if __name__ == '__main__':
    print_format_table()
    cprint("fuck egg", Fore.GREEN, Back.BLUE, Style.UNDERLINE)
