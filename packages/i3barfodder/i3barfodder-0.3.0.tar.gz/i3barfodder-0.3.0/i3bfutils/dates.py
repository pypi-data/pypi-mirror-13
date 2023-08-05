# Released under GPL3 terms (see LICENSE)

from i3bfutils import (io, cache)
import datetime
import re
import difflib
import operator

_NONSTD_MODULES = {}
try:
    from dateutil import easter
    _NONSTD_MODULES['dateutil'] = True
except ImportError:
    pass

# TODO: Add more date names.
DATENAMES = {
    # German holidays
    '01-01': ("New Year's Day",),
    '01-06': ("Three Kings' Day", 'Epiphany', 'Theophany'),
    '05-01': ('Labour Day', 'Labor Day'),
    '08-15': ('Assumption Day',),
    '10-03': ('Day of German Unity',),
    '10-31': ('Reformation Day', 'Halloween', "All Hallows' Eve"),
    '11-01': ("All Saints' Day", 'All Hallows', 'Solemnity of All Saints',
              'Feast of All Saints'),
    '12-25-5sun-1wed': ('Buß- und Bettag',),
    '12-25': ('Christmas',),
    '12-26': ("St. Stephen's Day", 'Boxing Day'),
    'EASTER': ('Easter', 'Easter Sunday', 'Resurrection Sunday'),
    'EASTER-2d': ('Good Friday', 'Holy Friday', 'Great Friday', 'Easter Friday'),
    'EASTER+1d': ('Easter Monday',),
    'EASTER+39d': ('Ascension Day', 'Ascension Thursday', 'Holy Thursday'),
    'EASTER+50d': ('Whit Monday', 'Pentecost Monday'),
    'EASTER+60d': ('Feast of Corpus Christi', 'Corpus Domini'),
}


class AlarmIndicator():
    """
    Given a list of alarm dates and a list of alarm indicator strings, provide
    the number of days until the next alarm date and an indicator string

    `dates` is a sequence of datetime.date objects.

    `alarmindicators` is a sequence of strings.  If today is in `dates`, the
    `indicator` property returns the first item, if tomorrow is in `dates`, it
    returns the second item, and so on.
    """
    def __init__(self, dates, alarmindicators):
        self._alarmindicators = tuple(alarmindicators)
        self._dates = tuple(sorted(dates))

    @property
    @cache.timeout(each='day')
    def days_until_alarm(self):
        """Days until next alarm date"""
        today = datetime.date.today()
        for date in self._dates:
            if date >= today:
                return (date - today).days
        return float('inf')

    @property
    @cache.timeout(each='day')
    def indicator(self):
        """String that indicates days until next alarm date"""
        predays = self.days_until_alarm
        if predays < len(self._alarmindicators):
            return self._alarmindicators[predays]
        else:
            return ''

    @property
    def dates(self):
        """List of alarm dates"""
        return self._dates

    def __len__(self):
        return len(self._dates)

    def __str__(self):
        return '; '.join(d.strftime('%Y-%m-%d') for d  in self._dates)

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self)


def str2dates(dates):
    """
    Convert `dates` to a tuple of unique dates for this and next year

    If `dates` is a string, each date must be separated by ';'.  Otherwise,
    `dates` must be a sequence of date strings.  See `str2date` for allowed
    date formats.
    """
    if isinstance(dates, str):
        datestrs = [ds.strip() for ds in dates.split(';') if ds != '']
    elif isinstance(dates, (list, tuple, set)):
        datestrs = list(dates)
    else:
        raise ValueError('Invalid type {!r}: {!r}'.format(type(dates).__name__, dates))

    # Calculate dates for this and next year.  This is the easiest way to
    # predict new year's day of the next year.
    dates = []
    thisyear = datetime.date.today().year
    for year in (thisyear, thisyear+1):
        dates += [str2date(datestr, year) for datestr in datestrs]

    # Remove duplicates
    return tuple(sorted(set(dates)))


# Flatten DATENAMES for easier access
_DATENAMES = dict((name,date)
                  for date,names in DATENAMES.items()
                  for name in names)

WEEKDAYS = { 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6, 'sun': 7,
             'mo': 1, 'tu': 2, 'we': 3, 'th': 4, 'fr': 5, 'sa': 6, 'su': 7 }

_DATE_REGEX = re.compile(r'^(?:(?P<year>\d{4})-)?'
                        r'(?P<month>\d{1,2})-'
                        r'(?P<day>\d{1,2})$')

_DELTA_REGEX = re.compile(r'(([\+-])(\d+)([a-z]{1,3}))+$', flags=re.IGNORECASE)

def str2date(datestr, year=datetime.date.today().year):
    """
    Parse `datestr` into datetime.date object

    The format of `datestr` is [YEAR-]MONTH-DAY.  If YEAR is not specified,
    the `year` argument is used, which defaults to the current year.

    `datestr` may also be a date name from `DATENAMES`.  As a last resort,
    `guess_datename` is used.

    All date formats can be adjusted with a delta::

        DATE[+-]<NUMBER><UNIT>

    For example, "2015-12-25+3d" adds 3 days, resulting in 2015-12-28.
    Allowed values for UNIT are "d" (days), "w" (weeks), and abbreviated
    weekday names (mo/mon, tu/tue, we/wed, th/thu, fr/fri, sa/sat, su/sun).
    If UNIT is a weekday, the date is adjusted to the NUMBERth next or
    previous weekday.  For example, "12-25-4sun" is the date of the 4th Sunday
    before Christmas (First Sunday of Advent).

    Multiple deltas are possible.

    The special string "EASTER" is replaced with the Easter date of `year`.
    """
    # Split datestr into date and delta
    datestr, delta_func_chain = _parse_delta(datestr)

    # Resolve names like "Christmas" to YYYY-MM-DD or MM-DD format
    datestr_ = datestr.lower()
    for name,date in _DATENAMES.items():
        if name.lower() == datestr_:
            datestr, dfuncs = _parse_delta(date)
            delta_func_chain.extend(dfuncs)
            datestr = _apply_easter(datestr, year)
            break

    # Parse datestr (YYYY-MM-DD or MM-DD) into date object
    match = _DATE_REGEX.match(datestr)
    if match is None:
        return str2date(guess_datename(datestr))
    else:
        date = datetime.date(int(match.group('year')) if match.group('year') else year,
                             int(match.group('month')),
                             int(match.group('day')))
        for delta_func in delta_func_chain:
            date = delta_func(date)
        return date

def _parse_delta(datestr):
    """
    Parse delta in `datestr`

    Return a tuple of the remaining date string and a list of callables that
    apply one delta each to any date.
    """
    delta_func_chain = []
    match = _DELTA_REGEX.search(datestr)
    if match is not None:
        deltastr = match.group(1)
        op = operator.add if match.group(2) == '+' else operator.sub
        num, unit = match.group(3, 4)
        datestr = datestr[:-len(deltastr)]
        delta_func_chain.append(
            lambda date: _apply_delta(date, op, int(num), unit))

        datestr, sub_chain = _parse_delta(datestr)
        delta_func_chain = sub_chain + delta_func_chain

    return datestr, delta_func_chain


def _apply_delta(date, op, num, unit):
    """
    Apply delta to `date`

    `op` must be `operator.add` or `operator.sub`, `num` must be an integer
    and `unit` must be "d", "w" or one of the keys in `WEEKDAYS`.
    """
    unit = unit.lower()
    if unit in WEEKDAYS:
        # `num`th weekday before/after `date`
        target_wday = WEEKDAYS[unit]
        date_wday = date.isoweekday()
        # print('Finding {}. {} ({}) {} {}, {} ({}):'
        #       .format(num, unit, target_wday,
        #               'after' if op == operator.add else 'before',
        #               date, [k for k,v in WEEKDAYS.items() if v == date_wday][0], date_wday))

        # Find delta to next/previous weekday
        if op is operator.sub:
            delta_wday = (7 - (target_wday - date_wday)) % 7
        elif op is operator.add:
            delta_wday = (7 - (date_wday - target_wday)) % 7

        # If date is on the targeted weekday, should we add/sub another week
        # or not?  If num is 0, the returned date may be the same as the
        # supplied date, otherwise a week is added/removed.
        if delta_wday == 0 and num != 0:
            delta_wday = 7
        # print('  Nearest {} {} {} is {} days away'.format(unit,
        #                                                   'after' if op == operator.add else 'before',
        #                                                   date, delta_wday))
        delta_weeks = max(0, num-1)
        delta_days = delta_wday + (delta_weeks*7)
        # print('  Adding {} weeks ({} days) = {} days'.format(delta_weeks, delta_weeks*7, delta_days))

    # Delta is an absolute number of days or weeks
    elif unit == 'w':
        delta_days = num * 7
    elif unit == 'd':
        delta_days = num

    else:
        opstr = '+' if op == operator.add else '-'
        io.croak('Invalid date delta: {}{}{}'.format(opstr, num, unit))

    old_date = date
    date = op(date, datetime.timedelta(days=delta_days))
    # print('  Final date: {}'.format(date))
    return date


@cache.timeout(each='eternity')
def _apply_easter(datestr, year):
    """Replaces "EASTER" in `datestr` with Easter date in `year`"""
    if 'dateutil' in _NONSTD_MODULES:
        if 'EASTER' in datestr:
            easterstr = easter.easter(year).strftime('%Y-%m-%d')
            datestr = datestr.replace('EASTER', easterstr)
        return datestr
    else:
        io.croak('Unable calculate Easter date without python-dateutil.')


@cache.timeout(each='eternity')
def guess_datename(string):
    """Fuzzy-find `string` in `DATENAMES`"""
    def distance(a, b):
        return difflib.SequenceMatcher(a=a, b=b).ratio()

    def simplify_datename(name):
        """Remove parts of date `name` that are common in many date names"""
        name = name.lower()
        name = ''.join(c for c in name if c in 'abcdefghijklmnopqrstuvwxyz')
        for part in ('day', 'feast', 'of'):
            name = name.replace(part, '')
        return name

    # Get distance from string to each date name
    distances = []
    _string = simplify_datename(string)
    for name,date in _DATENAMES.items():
        dist = distance(simplify_datename(name), _string)
        distances.append((dist, name))

    # Find best guess
    distances.sort()
    best_dist = distances[-1][0]
    best_guess = distances[-1][1]
    if best_dist < 0.6:
        io.croak('Unable to guess date: {!r}'.format(string))
    else:
        io.debug('Guessing {!r} means {} ({})'.format(string, best_guess, _DATENAMES[best_guess]))
        return best_guess
