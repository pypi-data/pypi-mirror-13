"""Functions that make useful keys"""

import re
import operator


def formatter(fmt, **kwargs):
    """Create a function that formats given values into strings.

    Additional keywoard arguments can be given that will also be passed to
    the format function.

    The values passed to the formatter will be given as the first argument
    to format, which is referenecd as {0}.

    """
    def formatted(val):
        return fmt.format(val, **kwargs)
    return formatted


_numberRegex = None


def numeric(value):
    """Split a string into string and integer sections.

    A string will be a tuple containing sections that are strings
    and integers. The numeric parts of the string will be converted
    into integers.

    This is a convenient way to sort string containing numbers that
    are not padded.

    Negative numbers will also be converted if preceded by a single
    minus sign.

    """
    global _numberRegex

    if not value:
        return ()

    if not _numberRegex:
        _numberRegex = re.compile("(-?\d+)")
    parts = _numberRegex.split(value)
    # Values that start with digits will get a leading empty string
    if value[0].isdigit():
        parts = parts[1:]
    if value[-1].isdigit():
        parts.pop()

    converted = tuple(int(p) if p[-1].isdigit() else p
                for p in parts)
    return converted


class _GetterImpl(object):
    """Shorthand for attrgetter and itemgetter operators.

    The same results can be achieved by using `operator.attrgetter` and
    `operator.itemgetter`, but this is more concise and can also be used
    to lookup nested data.

    If an attribute or item is not found this will result in None
    instead of an exception, which is more useful for key functions.

    You can lookup multiple items by passing multiple values to the
    index operator.

    Looking up attributes can only be done with a single value.

    >>> data = {"name": {"first": "Peter", "last": "Shinners"}, "id": 1234}
    >>> key = yter.key["name"]["first"]
    >>> print(key(data))
    "Peter"
    >>> print(yter.key.real(1.2))
    1.2

    """
    def __init__(self, getters):
        self.__getters = getters


    def __getitem__(self, vals):
        if isinstance(vals, tuple):
            getter = operator.itemgetter(*vals)
        else:
            getter = operator.itemgetter(vals)
        key = type(self)(self.__getters + (getter,))
        return key

    def __getattr__(self, name):
        getter = operator.attrgetter(name)
        key = type(self)(self.__getters + (getter,))
        return key

    def __call__(self, value):
        try:
            for getter in self.__getters:
                value = getter(value)
        except KeyError:
            return None
        except AttributeError:
            return None
        return value


getter = _GetterImpl(())
