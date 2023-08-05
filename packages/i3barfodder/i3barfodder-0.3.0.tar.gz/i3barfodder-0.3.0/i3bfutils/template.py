# Released under GPL3 terms (see LICENSE)

"""Create templates from strings"""

from . import io
from i3barfodder import util
from i3barfodder.validation import str2num
from i3barfodder.i3barproto import (I3Block, DynamicColor)
import re
import operator
from collections import abc


# TODO: Many popular status bar screenshots have labels in front of CPU,
# network, etc displays. Maybe Template should have a 'label' argument?


class Template():
    """Parser for layout strings to optimize output

    `layout` is a string that defines the blocks which are later used by
    `make_blocks`.

    `name` is an optional identifier.

    `dflt_limits` is a dictionary that maps the keys max/min/softmax/softman
    to dictionaries that map placeholders to numbers.

    Example::

        { 'max': { '{_percent}': 100,
                   '{_rate}': 1000000 },
          'min': { '{_percent}': -100,
                   '{_rate}': 0 } }
    """

    _SPLITBLOCKS_REGEX = re.compile(r'('
                                    r'(?<!\\)\[.*?(?<!\\)\]'  # [...] if brackets are not escaped
                                    r'[\d\|]*'                # Optional separator defintion
                                    r')')

    def __init__(self, layout, name=None, dflt_limits={}):
        self._blocks = []
        instance = 0
        for blockstr in self._SPLITBLOCKS_REGEX.split(layout):
            if blockstr == '':
                continue
            instance += 1

            # Enclose normal text with brackets to make it a valid block string
            if blockstr[0] != '[':
                blockstr = '[' + blockstr + ']'
            self._blocks.append(BlockTemplate(blockstr, str(name), str(instance), dflt_limits))

    def make_blocks(self, something, init=False):
        """
        Apply `something` to this template

        `something` can be:

          - a dictionary, which is passed to the `format` method of each
            string value of each block in this template. This creates a new
            list of blocks, which is returned.

          - a callable object, which is called with each string value of each
            block in this template to create a new list of blocks, which is
            returned.

          - a list/tuple/set of dictionaries/callables. In this case, each
            item is passed to this method recursively as described above. The
            resulting lists of blocks are concatenated (with `list.extend`)
            into a flat list and returned.

        If `init` is True, the returned blocks initialize things like dynamic
        colors and inline function calls (e.g. vbar()). If `init` is False,
        the returned blocks only update previously initialized blocks with new
        values.
        """
        if isinstance(something, (list, tuple, set)):
            result = []
            for s in something:
                result.extend(self.make_blocks(s, init))
            return result

        else:
            if callable(something):
                fillin = something
            else:
                something = dict(something)
                def fillin(tmplt_text):
                    try:
                        return tmplt_text.format(**something)
                    except KeyError as e:
                        io.croak('Unknown field: {}\nKnown fields are: {}'
                                 .format(e, ', '.join(something.keys())))

            return [block.apply(fillin, init=init)
                    for block in self._blocks]


class BlockTemplate():
    _BLOCK_REGEX = re.compile(r'^\['                       # Start of block
                              r'(?P<text>.*?)'             # This becomes 'full_text'
                              r'(?:(?<!\\)\|'              # After unescaped '|' ...
                              r'(?P<colorspec>[^\]]+?)'    # ... optional dynamic color
                              r')?'                        # End of dynamic color
                              r'\]'                        # End of block
                              r'(?P<separator>\|?\d*\|?)'  # Optional separator definition
                              r'$')

    def __init__(self, blockstr, name=None, instance=None, dflt_limits={}):
        self._update_template = {}
        if name is not None:
            self._update_template['name'] = name
        if instance is not None:
            self._update_template['instance'] = instance

        self._init_template = self._update_template.copy()
        self._init_template.update(separator=False, separator_block_width=0)

        blockmatch = self._BLOCK_REGEX.match(blockstr)
        if blockmatch is None:
            raise ValueError('Invalid block template string: {!r}'.format(blockstr))

        full_text = unescape(blockmatch.group('text'), chars='[]|')
        full_text_init, full_text_update = _optimize_function_calls(full_text, dflt_limits)
        self._init_template['full_text'] = full_text_init
        self._update_template['full_text'] = full_text_update

        # Optional dynamic color specification
        colorspec = blockmatch.group('colorspec')
        if colorspec is not None:
            dyncolor_spec, dyncolor_value = _optimize_dyncolor(colorspec, dflt_limits)
            self._init_template['color'] = dyncolor_spec
            if dyncolor_value is not None:
                self._update_template['dyncolor_value'] = dyncolor_value

        # 'separator' and 'separator_block_width'
        sep = blockmatch.group('separator')
        self._init_template['separator'] = bool(sep and (sep[0] == '|' or sep[-1] == '|'))
        sep = sep.strip('|')
        if sep:
            # The regex matches only \d and |, so it should be save to not
            # catch any errors here.
            self._init_template['separator_block_width'] = int(sep)

        # io.debug('INIT: {}'.format(self._init_template))
        # io.debug('UPDATE: {}'.format(self._update_template))

    def apply(self, callback, init):
        """
        Use `callback` to create a new block

        Pass each string value in the template to `callback` and use its
        return value to replace the string.  This creates a new block that is
        finally returned.  Non-string values are copied shallowly.

        If `init` is True, initialize dynamic colors, vbars, etc. Otherwise
        just update them.
        """
        if init:
            block = self._init_template.copy()
        else:
            block = self._update_template.copy()

        for key,val in block.items():
            if type(val) is str:
                try:
                    block[key] = ConditionalString(callback(val))
                except ConditionError as e:
                    io.croak(e)
                except Exception as e:
                    import traceback
                    import pprint
                    io.debug(traceback.format_exc())
                    io.croak('Unknown fatal error while working on template:\n{}'
                             .format(pprint.pformat(block)))

        # io.debug('Made a new block: {}\n'.format(block))
        return block


def _optimize_function_calls(text, dflt_limits={}):
    def make_init_call(funcname, callid, argstr):
        kwargs = I3Block.INLINE_FUNCTIONS[funcname].parse_args(argstr)
        kwargs_dct = dict(kwargs)
        init_args = []

        # Defaults
        for key in dflt_limits.keys():
            field = kwargs_dct['value']
            if 'value' in kwargs_dct and field in dflt_limits[key]:
                init_args.append('{}={}'.format(key, dflt_limits[key][field]))

        # Appending user arguments overrides any defaults
        for key,value in kwargs_dct.items():
            init_args.append('{}={}'.format(key, value))

        callstr = '{}{}({})'.format(funcname, callid, ', '.join(init_args))
        # io.debug('Made new init call: {}'.format(callstr))
        return callstr

    def make_update_call(funcname, callid, argstr):
        kwargs = dict(I3Block.INLINE_FUNCTIONS[funcname].parse_args(argstr))
        if 'value' in kwargs:
            callstr = '{}{}({})'.format(funcname, callid, kwargs['value'])
        else:
            callstr = '{}{}()'.format(funcname, callid)
        # io.debug('Made new update call: {}'.format(callstr))
        return callstr

    init_text = util.parse_function_calls(text, I3Block.INLINE_FUNCTION_NAMES,
                                          make_init_call)
    update_text = util.parse_function_calls(text, I3Block.INLINE_FUNCTION_NAMES,
                                            make_update_call)
    return init_text, update_text


def _optimize_dyncolor(dyncolorstr, dflt_limits={}):
    """
    Prepend default limits (min, max, etc) to dynamic color specification `dyncolorstr`

    Return the resulting full dynamic color string and the value (typically a
    placeholder) to update it, or None if no value is specified.
    """
    # io.debug('Parsing dynamic color string: {}'.format(dyncolorstr))
    try:
        usr_spec = DynamicColor.parse(dyncolorstr)
    except Exception as e:
        io.croak('Error while parsing dynamic color {!r}: {}'.format(dyncolorstr, e))
    else:
        # For each user-provided key=value pair, value might be a placeholder
        # string (e.g. '{_read%}').  Lookup that placeholder's default limits
        # in dflt_limits and prepend it to the user-provided pairs.  This
        # allows the user to override default limits.
        # dflt_limits might look like this:
        # { 'min':    {'{_read}':0,'{_write}':0, '{_free%}':0},
        #   'softmax: {'{_read}':'100M', '{_write}':'100M'},
        #   'max:     {'{_free%}':100} }
        dflt_spec = []
        value_field = None
        for key,field in usr_spec:
            if key == 'value':
                value_field = field
            for name,limits in sorted(dflt_limits.items()):
                if field in limits:
                    dflt_spec.append((name, limits[field]))
        final_spec = tuple(dflt_spec) + usr_spec
        final_spec_str = ':'.join('{}={}'.format(k,v) for k,v in final_spec)
        # io.debug('Optimized dyncolor string: {!r}, {!r}'.format(final_spec_str, value_field))
        return final_spec_str, value_field


class ConditionError(Exception):
    pass

class ConditionalString(str):
    """
    Normal string that resolves and replaces conditions before instantiation

    A condition may appear anywhere in the string and looks like this::

        (SOMETHING?[=]CONDITION)

    The condition is replaced with SOMETHING if CONDITION is true.  If the "?"
    is followed by a "=", the condition is replaced with the result of
    ``len(SOMETHING)*' '``.

    CONDITION compares two numbers and uses `i3barfodder.str2num` to parse
    them. Comparison operators are: "<", ">", "<=", ">=", "=", "!="

    Escaping "(" or ")" prevents the condition from being parsed.
    """
    def __new__(cls, string):
        # io.debug('Parsing conditions in: {!r}'.format(string))
        if '(' not in string:
            return string
        while True:
            start, end = cls._find_next_condition(string)
            if start is not None:
                replacement = cls._apply_condition(string[start:end])
                string = ''.join((string[:start], replacement, string[end:]))
            else:
                return unescape(string, chars='()?')

    @staticmethod
    def _find_next_condition(string):
        start = -1
        for i,c in enumerate(string):
            if c == '(' and (i == 0 or string[i-1] != '\\'):
                start = i
            elif c == ')' and start >= 0 and string[i-1] != '\\':
                end = i+1
                if '?' in string[start:end]:
                    return (start, end)
        return (None, None)

    _CONDITION_REGEX = re.compile(r'^(?<!\\)\('
                                  r'(?P<text>.*?)'                 # full_text
                                  r'(?<!\\)\?(?P<fixedwidth>=?)'   # '?' or '?='
                                  r'(?P<value1>.+?)'               # first int/float
                                  r'(?P<operator>[<>=!]+)'         # operator
                                  r'(?P<value2>.+?)'               # second int/float
                                  # TODO: Add an optional 'else' separated by a ':'.
                                  r'(?<!\\)\)$')

    _CMP_OPS = { '<': operator.lt, '>': operator.gt,
                 '<=': operator.le, '>=': operator.ge,
                 '=': operator.eq, '!=': operator.ne }

    @classmethod
    def _apply_condition(cls, conditionstr):
        match = cls._CONDITION_REGEX.match(conditionstr)
        if match is None:
            raise ConditionError("Invalid condition: '{}'".format(conditionstr))
        else:
            op = match.group('operator')
            if op not in cls._CMP_OPS:
                raise ConditionError(("Invalid comparison operator in condition "
                                      "'{}': '{}'").format(conditionstr, op))
            else:
                op = cls._CMP_OPS[op]
                text = match.group('text')
                fixedwidth = match.group('fixedwidth')
                values = []
                for val in match.group('value1', 'value2'):
                    try:
                        values.append(str2num(val))
                    except ValueError:
                        raise ConditionError(("Non-number comparison in condition "
                                              "'{}': '{}'").format(conditionstr, val))

                if op(*values):
                    return text
                elif fixedwidth:
                    return ' '*len(text)
                else:
                    return ''


def unescape(string, chars=''):
    """Remove backslash in front of any character in `string` that is in `chars`"""
    if '\\' in string:
        for c in chars:
            string = string.replace('\\'+c, c)
    return string


class PrettyDict(abc.MutableMapping):
    """
    Dictionary that keeps raw and human-readable values

    Only raw values (e.g. 1000000) can be set. Those values are converted to a
    human-readable string (e.g. '1M') when requested. This is done by passing
    raw values to user-supplied prettifier callables.

    >>> pd = PrettyDict(prettifiers={'percentage': lambda p: '{:.0f}%'.format(p*100)})
    >>> pd['percentage'] = 0.3412
    >>> pd['percentage']
    '34%'

    To get raw values, '_' must be prepended to the key:

    >>> pd['_percentage']
    0.3412

    When setting values, it doesn't matter if there's a leading '_' or not.

    >>> pd['_percentage'] = 0.3412
    >>> pd['percentage']
    '34%'
    >>> pd['percentage'] = 34
    >>> pd['percentage']
    '3400%'

    If a key is not a string, the raw value is always returned.

    The default prettifier is `str`.
    """
    def __init__(self, prettifiers={}, **initial_values):
        self._prettifiers = prettifiers
        self._values_raw = {}
        self._values_pretty = {}
        self.update(initial_values)

    @property
    def prettifiers(self):
        """Dictionary that maps keys to callables"""
        return self._prettifiers

    @staticmethod
    def _real_key(key):
        """Strip the leading '_' if `key` is string'"""
        return key[1:] if isinstance(key, str) and key[0] is '_' else key

    def __setitem__(self, key, value):
        key = self._real_key(key)
        self._values_raw[key] = value
        self._invalidate(key)

    def _invalidate(self, key):
        """Forget prettification of `key`'s value"""
        if key in self._values_pretty:
            del self._values_pretty[key]

    def __getitem__(self, key):
        return_raw_value = not isinstance(key, str) or key[0] is '_'
        key = self._real_key(key)
        value = self._values_raw[key]
        if callable(value):
            value = value()
            self._invalidate(key)

        if return_raw_value:
            return value
        else:
            if key in self._values_pretty:
                # Use cached prettification
                return self._values_pretty[key]
            else:
                if key in self._prettifiers:
                    self._values_pretty[key] = self._prettifiers[key](value)
                else:
                    self._values_pretty[key] = str(value)
            return self._values_pretty[key]

    def __delitem__(self, item):
        key = self._real_key(item)
        del self._values_raw[key]
        if key in self._values_pretty:
            del self._values_pretty[key]

    def __iter__(self):
        keys_pretty = self._values_raw.keys()
        keys_raw = ('_'+key for key in keys_pretty)
        return (k for pair in zip(keys_pretty, keys_raw)
                for k in pair)

    def __len__(self):
        return len(tuple(iter(self)))

    def __repr__(self):
        items = []
        for k,v in self._values_raw.items():
            raw_val = v() if callable(v) else v
            items.append('{}={}={}'.format(k, raw_val, repr(self[k])))
        return '<{} {}>'.format(type(self).__name__, ', '.join(items))
