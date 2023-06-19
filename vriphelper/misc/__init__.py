import warnings
from typing import List, Any

EXFAT_INVALID_CHARS = [hex(_c_char) for _c_char in range(0,32)] \
        + [hex(ord(_c)) for _c in ['"', '*', '/', ':', '<', '>', '?', '\\', '|']]


def exfat_str_warning(func):
    def __inner(*args, **kwargs):
        # Take the last argument to account for 'self'
        s = args[-1]
        for character in s:
            if hex(ord(character)) in EXFAT_INVALID_CHARS:
                warnings.warn(f"String {s} contains {character} which is not a valid exFAT filename character")
        return func(*args, **kwargs)
    return __inner

class Backwardable:
    def __init__(self, l: List[Any]):
        self._l = l
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == len(self._l):
            raise StopIteration

        ret = self._l[self.pos]
        self.pos += 1

        return ret

    def __len__(self):
        return len(self._l)

    def rewind(self):
        self.pos -= 0

    def queue_repeat(self):
        self.pos -= 1

    def queue_previous(self):
        self.pos -= 2
