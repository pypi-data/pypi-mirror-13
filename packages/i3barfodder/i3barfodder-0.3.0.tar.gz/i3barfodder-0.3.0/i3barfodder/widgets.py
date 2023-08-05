# Released under GPL3 terms (see LICENSE file)

from . import (util, validation)
import logging


class VerticalBar():
    """Use unicode characters to create a vertical bar"""

    CHARS = (
        '\u0020', # ' '
        '\u2581', # '▁'
        '\u2582', # '▂'
        '\u2583', # '▃'
        '\u2584', # '▄'
        '\u2585', # '▅'
        '\u2586', # '▆'
        '\u2587', # '▇'
        '\u2588', # '█'
    )
    MAX_INDEX = len(CHARS)-1

    ARGS = ('value', 'min', 'max', 'softmin', 'softmax', 'scale')

    @classmethod
    def parse_args(cls, argstr):
        posargs, kwargs = util.parse_args(argstr)
        return util.pos2kwargs(posargs, kwargs, keys=cls.ARGS)

    def __init__(self, *kwargs):
        self._ratio = util.Ratio(*kwargs)
        self._current_str = self._get_str()

    def update(self, *kwargs):
        self._ratio.update(*kwargs)
        self._current_str = self._get_str()
        return self._current_str

    def _get_str(self):
        index = round(self.MAX_INDEX * float(self._ratio))
        return self.CHARS[index]

    def copy(self):
        copy = type(self)()
        copy._ratio = self._ratio.copy()
        copy._current_str = self._current_str
        return copy

    def __str__(self):
        return self._current_str


class HorizontalBar(VerticalBar):
    """Use unicode characters to create a horizontal bar"""

    CHARS = (
        '\u0020', # ' '
        '\u258F', # '▏'
        '\u258E', # '▎'
        '\u258D', # '▍'
        '\u258C', # '▌'
        '\u258B', # '▋'
        '\u258A', # '▊'
        '\u2589', # '▉'
        '\u2588', # '█'
    )
    MAX_INDEX = len(CHARS)-1

    ARGS = ('value', 'width', 'min', 'max', 'softmin', 'softmax', 'scale')

    def __init__(self, *kwargs):
        self._width = 1
        ratio_args = []
        for k,v in kwargs:
            if k == 'width':
                self._width = validation.validate_integer(v, min=1)
            else:
                ratio_args.append((k,v))
        self._ratio = util.Ratio(*ratio_args)
        self._current_str = self._get_str()

    def _get_str(self):
        value = float(self._ratio)
        filled_len = int(self._width * value)
        filled_str = self.CHARS[-1] * filled_len

        # To calculate which CHAR to append, first find `value` for the
        # previous and next full block.
        prev_value = max(0, (filled_len) / self._width)
        if value != prev_value:
            next_value = min(1, (filled_len+1) / self._width)

            # Where is `value` in relation to next and previous block?
            rest = value - prev_value

            # How much `value` must increase per CHAR
            stepsize = (next_value - prev_value) / self.MAX_INDEX
            index = round(rest / stepsize)
            filled_str += self.CHARS[index]

        empty_str = self.CHARS[0] * (self._width - len(filled_str))
        return filled_str+empty_str
