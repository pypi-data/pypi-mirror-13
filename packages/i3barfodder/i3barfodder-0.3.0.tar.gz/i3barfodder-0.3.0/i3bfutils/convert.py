# Released under GPL3 terms (see LICENSE)

"""Various conversion functions"""

from . import io
from i3barfodder.util import str2num


_UNIT_PREFIXES = {
    2: ( ('Ti', 1024**4), ('Gi', 1024**3), ('Mi', 1024**2), ('Ki', 1024) ),
    10: ( ('T', 1000**4), ('G', 1000**3), ('M', 1000**2), ('k', 1000) ),
}
def num2str(num, binary=False):
    """
    Add SI prefix to the number `num`

    >>> num2str((1024**3)*10, binary=True)
    '10 Gi'
    >>> num2str(1500, binary=False)
    '1.5 k'
    """
    powerof = 2 if binary else 10
    prefixes = _UNIT_PREFIXES[powerof]
    for prefix,size in prefixes:
        if num >= size:
            num = round(num / size, 1)
            frmt = '{n:.0f} {p}'
            if num < 10 and num % 1 != 0:
                frmt = '{n:.1f} {p}'
            return frmt.format(n=num, p=prefix)
    return '{:.0f} '.format(num)


def str2bits(string):
    """
    Convert bytes or bits to bits depending on unit ('b' or 'B')

    >>> str2bits('1kB')
    8000
    >>> str2bits('1 Kib/s')
    1024
    >>> str2bits('4.3 Gi')
    4617089843.2
    """
    string = string.strip()
    if string.endswith('/s'):
        string = string[:-2]
    if string.endswith('B'):
        return str2num(string) * 8
    else:
        return str2num(string)  # Assume bits

def str2bytes(string):
    """Same as `str2bits`, but convert to bytes"""
    string = string.strip()
    if string.endswith('/s'):
        string = string[:-2]
    if string.endswith('b'):
        return str2num(string) / 8
    else:
        return str2num(string)  # Assume bytes


def percent2num(value):
    """
    Return percentage as float or integer

    >>> percent2num('58.2 %')
    58.2
    >>> percent2num('147%')
    147
    >>> percent2num('0.1%')
    0.1
    """
    if isinstance(value, str):
        value = value.strip()
        if value.endswith('%'):
            value = value[:-1]
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                io.croak('Invalid percent notation: {!r}'.format(value))
    return value

def num2percent(num):
    """
    Return `num` (float or int) as human-readable percentage

    >>> num2percent(7.3188)
    '  7%'
    """
    return '{:3.0f}%'.format(float(num))
