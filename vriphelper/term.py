import tty
import os
import sys
import rich
from enum import Enum
from rich.console import Console
from rich.table import Table
from typing import Optional, List, Any

def getch() -> str:
    fd = 0
    old_term_attr = tty.tcgetattr(fd)

    try:
        term_attr = tty.tcgetattr(fd)
        term_attr[tty.LFLAG] &= ~(tty.ECHO | tty.ICANON)
        term_attr[tty.CC][tty.VMIN] = 3
        term_attr[tty.CC][tty.VTIME] = 1
        tty.tcsetattr(fd, tty.TCSAFLUSH, term_attr)
        return os.read(fd, 3)
    finally:
        tty.tcsetattr(fd, tty.TCSADRAIN, old_term_attr)

class ReorderableTable:
    class Keys(Enum):
        UP    = bytes("\x1b[A", 'ascii')
        DOWN  = bytes("\x1b[B", 'ascii')
        SPACE = bytes(" ", 'ascii')

    def __init__(self, title: str, columns: List[str], rows: List[list]):
        self.title = title
        self.columns = columns
        self.rows = list(rows)

        self._current_idx = 0
        self._selected = False
        self._initialized = False
        self._console = Console()

    def _get_table(self):
        t = Table(title=self.title, title_style="", box=rich.box.HORIZONTALS)

        for idx, column in enumerate(self.columns):
            t.add_column(
                    column,
                    justify="right" if idx in [0, len(self.columns)] else "",
                    no_wrap=True if idx == 0 else False
                    )

        for idx, row in enumerate(self.rows):
            row_style = ""
            if idx == self._current_idx:
                if self._selected:
                    row_style = "black on yellow"
                else:
                    row_style = "on green"

            t.add_row(*[str(e) for e in row], style=row_style)

        return t

    def inquire(self):
        while True:
            if self._initialized:
                for i in range(0, len(self.rows)+5):
                    sys.stdout.write(chr(27) + "[1A") # move cursor up one line
                    sys.stdout.write(chr(27) + "[K") # clear the line

            self._console.print(self._get_table())
            self._initialized = True

            try:
                key = getch()
            except KeyboardInterrupt:
                break

            if key == self.Keys.UP.value and self._current_idx != 0:
                self._current_idx -= 1
                if self._selected:
                    self.rows.insert(
                            self._current_idx, self.rows.pop(self._current_idx + 1)
                            )
            elif key == self.Keys.DOWN.value and self._current_idx < len(self.rows) - 1:
                self._current_idx += 1
                if self._selected:
                    self.rows.insert(
                            self._current_idx, self.rows.pop(self._current_idx - 1)
                            )
            elif key == self.Keys.SPACE.value:
                self._selected = not self._selected
