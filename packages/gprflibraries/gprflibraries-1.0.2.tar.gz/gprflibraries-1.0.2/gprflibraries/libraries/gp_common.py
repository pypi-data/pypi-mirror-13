"""
GP python common keywords.
"""


def strip_string(string, chars=None):
    """
    Return a copy of the string with leading and trailing whitespace removed.
    If chars is given and not None, remove characters in chars instead.

    Usage:
    | strip string | " test test " |
    returns "test test"

    | strip string | tttessttt | t |
    returns ess
    """

    return string.strip(chars)


def strip_string_left(string, chars=None):
    """
    Return a copy of the string with leading whitespace removed.
    If chars is given and not None, remove characters in chars instead.

    Usage:
    | strip string left | " test test " |
    returns "test test "

    | strip string left | tttessttt | t |
    returns essttt
    """

    return string.lstrip(chars)


def strip_string_right(string, chars=None):
    """
    Return a copy of the string with trailing whitespace removed.
    If chars is given and not None, remove characters in chars instead.

    Usage:
    | strip string right | " test test " |
    returns " test test"

    | strip string right | tttessttt | t |
    returns tttess
    """

    return string.rstrip(chars)


def convert_to_title(string):
    """
    Return a string as title

    Usage:
    | convert to title | "this is title" |
    returns "This Is Title"
    """

    return string.title()
