# Released under GPL3 terms (see LICENSE file)

from . import (widgets, validation, error)
from . import util
import re
import json
import logging
import sys
from copy import deepcopy


class I3Stdout():
    """Wrapper for sys.stdout that optimizes printing to i3bar"""

    _initialized = False
    _HEADER = json.dumps({ 'version': 1, 'click_events': True }) + '\n[[],\n'

    def write(self, b):
        if not self._initialized:
            sys.__stdout__.write(self._HEADER)
            self._initialized = True
        sys.__stdout__.write(b)
        sys.__stdout__.flush()

    def __getattr__(self, name):
        return getattr(sys.__stdout__, name)


class I3Block():
    DEFAULTS = {
        'full_text': '',
    }

    VALIDATORS = {
        'align': lambda v: validation.validate_option(v, ('left', 'right', 'center')),
        'instance': lambda v: str(v),
        'markup': lambda v: validation.validate_option(v, ('pango', 'none')),
        'min_width': lambda v: validation.validate_integer(v, min=0),
        'name': lambda v: str(v),
        'separator': validation.validate_bool,
        'separator_block_width': lambda v: validation.validate_integer(v),
        'urgent': validation.validate_bool,

        # These need an instance and are therefore specified in __init__()
        'full_text': None,
        'short_text': None,
        'color': None,
    }

    VALID_FIELDS = tuple(VALIDATORS) + \
                   tuple('dyncolor_'+k for k in ('colors', 'value', 'min', 'max',
                                                 'softmin', 'softmax', 'scale'))

    # TODO: Add more functions:
    #   - graph(): list of vertical bars that shift their values from
    #              right to left over time
    INLINE_FUNCTIONS = { 'vbar': widgets.VerticalBar,
                         'hbar': widgets.HorizontalBar }
    INLINE_FUNCTION_NAMES = tuple(INLINE_FUNCTIONS)

    def __init__(self, **initial_vars):
        self._errors = []
        self._dyncolor = DynamicColor()
        self._use_dyncolor = False
        self._funcs = dict((funcname, {})
                           for funcname in self.INLINE_FUNCTIONS.keys())

        def parse_fn_calls(text):
            return util.parse_function_calls(text, self.INLINE_FUNCTION_NAMES, self._call_function)

        validators = self.VALIDATORS.copy()
        validators.update(full_text=parse_fn_calls,
                          short_text=parse_fn_calls,
                          color=self._parse_color)

        self._i3vars = validation.VDict(validators=validators,
                                        valid_keys=tuple(validators),
                                        **self.DEFAULTS)
        self.update(**initial_vars)

    def _call_function(self, funcname, callid, argstr):
        callids = self._funcs[funcname]
        try:
            if callid in callids:
                func = callids[callid]
                func.update(*func.parse_args(argstr))
            else:
                try:
                    func = self.INLINE_FUNCTIONS[funcname]
                except KeyError:
                    self._errors.append('Unknown function: {}'.format(funcname))
                    return '!'
                else:
                    callids[callid] = func(*func.parse_args(argstr))

        except error.InvalidKey as e:
            self._errors.append("Invalid {} argument: '{}'".format(funcname, e))
            return '!'
        except error.InvalidValue as msg:
            self._errors.append('Invalid {} argument: {}'.format(funcname, msg))
            return '!'
        else:
            return str(callids[callid])

    @property
    def json(self):
        if self._use_dyncolor and self._dyncolor:
            i3vars = dict(self._i3vars)
            i3vars['color'] = str(self._dyncolor)
            return json.dumps(i3vars)
        else:
            return json.dumps(self._i3vars)

    @property
    def errors(self):
        errors = list(self._errors)
        self._errors = []
        return errors

    def copy(self):
        copy = type(self)(**self._i3vars)
        copy._dyncolor = self._dyncolor.copy()
        copy._funcs = deepcopy(self._funcs)
        return copy

    def update(self, **dct):
        if 'color' in dct and 'dyncolor_value' in dct:
            self._errors.append("Specifying both 'color' and 'dyncolor_value' is ambiguous.")
        else:
            for key,value in dct.items():
                try:
                    self[key] = value
                except error.Validation as e:
                    self._errors.append(str(e))

    def __setitem__(self, key, value):
        try:
            if key.startswith('dyncolor_'):
                arg_key = key[9:]  # Remove 'dyncolor_'
                self._dyncolor[arg_key] = value
                self._use_dyncolor = True
            else:
                self._i3vars[key] = value
                if key == 'color':
                    self._use_dyncolor = False
        except error.InvalidKey as invalid_key:
            self._errors.append('Invalid field: {}'.format(invalid_key))
        except error.InvalidValue as e:
            self._errors.append('{}: {}'.format(key, e))

    def __getitem__(self, key):
        if key == 'color' and self._use_dyncolor and bool(self._dyncolor):
            return str(self._dyncolor)
        try:
            return self._i3vars[key]
        except error.InvalidKey as invalid_key:
            self._errors.append('Invalid field: {}'.format(invalid_key))

    def __delitem__(self, key):
        try:
            del(self._i3vars[key])
        except error.InvalidKey as invalid_key:
            self._errors.append('Invalid field: {}'.format(invalid_key))

    def __contains__(self, key):
        return key in self._i3vars

    def __eq__(self, other):
        if isinstance(other, type(self)):
            for attr in ('_i3vars', '_dyncolor', '_funcs'):
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        else:
            return NotImplemented

    def __repr__(self):
        r = '<{} '.format(type(self).__name__)
        r += ', '.join('{}={!r}'.format(k, v)
                       for k,v in sorted(self._i3vars.items()))
        if self._dyncolor:
            r += ', ' + repr(self._dyncolor)
        return r+'>'

    def _parse_color(self, string):
        """
        Set 'color' variable to fixed or dynamic color

        `string` is passed to `RGBColor`.  If that fails, it is passed to
        `DynamicColor.parse` to update the internal dynamic color.

        Returns the current color as an RGB string.
        """
        string = str(string)
        try:
            return str(RGBColor(string))
        except error.InvalidValue:
            self._dyncolor.update(*self._dyncolor.parse(string))
            return str(self._dyncolor)


class RGBColor():
    """Mixable RGB color"""

    HEXCHARS = '0123456789abcdefABCDEF'

    def __init__(self, rgb):
        if not isinstance(rgb, str) or \
           len(rgb) not in (7, 4) or \
           not rgb.startswith('#') or \
           not all(c in self.HEXCHARS for c in rgb[1:]):
            raise error.InvalidValue('Invalid RGB color: {!r}'.format(rgb))
        rgb = rgb.lstrip('#')
        if len(rgb) == 3:
            # Convert 3-digit notation to 6-digit notation
            rgb = rgb[0]+rgb[0] + rgb[1]+rgb[1] + rgb[2]+rgb[2]
        self.r = int(rgb[0:2], 16)
        self.g = int(rgb[2:4], 16)
        self.b = int(rgb[4:6], 16)

    def combine(self, other, factor):
        cls_self = type(self)
        cls_other = type(other)
        if not cls_self == cls_other:
            raise error.InvalidValue('Cannot combine {!r} ({}) and {!r} ({})'
                                     .format(self, cls_self.__name__,
                                             other, cls_other.__name__))
        rgb = '#'
        for col in ('r', 'g', 'b'):
            # I don't really understand the '* (256/255)' part, but the
            # maximum 0xff is 255, and fracturing that is "wrong" (255*0.5 is
            # 127.5, not 128 (0x80)), and what I'm doing here "elevates" all
            # values to a maximum of 256, even though they stay mostly the
            # same. (Also, I suck at math.)
            val_other = getattr(other, col) * (256/255)
            val_self = getattr(self, col) * (256/255)
            val_new = max(0, min(255, ((val_other*factor) + (val_self*(1-factor)))))
            rgb += '{:02X}'.format(round(val_new))
        return cls_self(rgb)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.r == other.r and
                    self.g == other.g and
                    self.b == other.b)
        else:
            # Maybe other is RGB string?
            try:
                other = type(self)(other)
            except:
                return False
            else:
                return repr(self) == repr(other)

    def __str__(self):
        return '#' + ''.join(['%02X' % c for c in (self.r, self.g, self.b)])

    __repr__ = __str__


class DynamicColor():
    """Create new RGB colors from a list of RGB colors based on `util.Ratio`"""

    KEYS = ('value', 'colors', 'min', 'max', 'softmin', 'softmax', 'scale')

    @classmethod
    def parse(cls, string):
        """
        Return a tuple of (key, value) tuples that can be passed to `DynamicColor.update`

        `string` is a list of parameters separated by ':'.

        Valid parameters are:
          - colors=<list of RGB colors, separated by '-'> ('colors=' is optional)
          - value=number (int or float; 'value=' is optional)
          - [min|max|softmin|softmax]=<number> (int or float)
          - scale=[linear|sqrt|log]

        Example: value=25:colors=#ff0000-#0f0-#0000ff:min=0:softmax=100
        """
        pos, kw = util.parse_params(string)

        # The first two positional arguments ('value' and 'colors') don't need
        # a key and may even switch places, so we have to be clever here.
        if pos:
            pos_len = len(pos)
            first_arg = pos[0]
            first_arg_is_colors = type(first_arg) is str and first_arg[0] == '#'
            if pos_len == 1:
                # Convert single positional argument to keyword argument
                if first_arg_is_colors:
                    kw = (('colors', first_arg),) + kw
                else:
                    kw = (('value', first_arg),) + kw
                pos = pos[1:]

            elif pos_len >= 2 and first_arg_is_colors:
                # Switch first two positional arguments if the first one is 'colors'
                pos = (pos[1], pos[0]) + pos[2:]

        return util.pos2kwargs(pos, kw, keys=cls.KEYS)

    def __init__(self, *settings):
        self._colors = ()
        self._color_num = 0
        self._max_color_index = -1
        self._ratio = util.Ratio()
        self._cache = {}
        self._current_color = ''
        self.update(*settings)

    def update(self, *settings):
        try:
            for k,v in settings:
                self[k] = v
        except ValueError:
            raise error.InvalidValue('not an iterable of key-value pairs: {!r}'.format(settings))
        return str(self)

    def _mix_new_color(self, value):
        i_max = self._max_color_index
        if i_max < 0:
            self._current_color = ''
        else:
            # Find the two relevant colors
            if self._color_num == 2:
                color_min, color_max = self._colors
                i1, i2 = 0, 1
            else:
                fraction = value / 100
                i2 = min(i_max, round((i_max * fraction) + 0.50000001))
                i1 = i2-1
                color_min = self._colors[i1]
                color_max = self._colors[i2]

            # Figure out where value is between its limits
            value_min = 100 * ( float(i1) / i_max)
            value_max = 100 * ( float(i2) / i_max)
            factor = (value - value_min) / (value_max - value_min)

            # Combine the two colors
            self._current_color = str(color_min.combine(color_max, factor))
            self._cache[value] = self._current_color
        return self._current_color

    def __getitem__(self, item):
        if item == 'color':
            return self._current_color
        elif item == 'colors':
            return tuple(str(c) for c in self._colors)
        else:
            return self._ratio[item]

    def __setitem__(self, item, value):
        if item == 'colors':
            if isinstance(value, str):
                value = tuple(value.split('-'))
            elif isinstance(value, (list, tuple, set)):
                value = tuple(value)
            else:
                raise error.InvalidValue("'color' value must be string or sequence, not {}: {!r}"
                                         .format(type(value).__qualname__, value))
            if value != self._colors:
                new_colors = []
                for c in value:
                    if isinstance(c, RGBColor):
                        new_colors.append(c)
                    else:
                        new_colors.append(RGBColor(c.strip()))
                self._colors = tuple(new_colors)
                self._color_num = len(self._colors)
                self._max_color_index = self._color_num-1
                self._cache = {}
        else:
            self._ratio[item] = value

    def copy(self):
        copy = type(self)(('colors', tuple(str(c) for c in self._colors)))
        copy._color_num = self._color_num
        copy._max_color_index = self._max_color_index
        copy._ratio = self._ratio.copy()
        copy._cache = self._cache.copy()
        copy._current_color = self._current_color
        return copy

    def __str__(self):
        if self._color_num < 1:
            self._current_color = ''
        elif self._color_num == 1:
            self._current_color = str(self._colors[0])
        else:
            value = round(self._ratio.as_percent)
            try:
                self._current_color = self._cache[value]
            except KeyError:
                self._mix_new_color(value)
                # logging.info('Created color for value={} -> {}'.format(value, self._current_color))
        return self._current_color

    def __repr__(self):
        r = '-'.join(str(c) for c in self._colors)
        if self._ratio['min'] != 0:
            if self._ratio.min_is_soft:
                r += ':softmin={}'.format(self._ratio['min'])
            else:
                r += ':min={}'.format(self._ratio['min'])
        if self._ratio['max'] != 0:
            if self._ratio.max_is_soft:
                r += ':softmax={}'.format(self._ratio['max'])
            else:
                r += ':max={}'.format(self._ratio['max'])
        r += ':{}'.format(self._ratio['value'])
        return r

    def __eq__(self, other):
        if isinstance(other, type(self)):
            for attr in ('_colors', '_ratio', '_current_color'):
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        else:
            return NotImplemented

    def __bool__(self):
        return str(self) != ''
