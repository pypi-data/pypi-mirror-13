"""
String utilities.
"""


def trim(value, default_value=''):
    """
    Removes leading and trailing whitespace from the specified string. If the specified string is composed of
    whitespace only, the specified default value is returned.

    :param value: a string to trim
    :param default_value: a default value to return if the specified string consists of whitespace only.
    :return: a string without any leading or trailing whitespace or the specified default value if
        the specified string consists of whitespace only.
    """
    value = value.strip() if value else None
    return value if value else default_value


def ensure_not_blank(value, message=None):
    """
    Removes leading and trailing whitespace from the specified string and checks whether or not
    it is blank (None or whitespace). If it is, it raises a `ValueError` with the specified `message`.

    :param value: value to check
    :param message: message to pass to ValueError
    :raises ValueError
    """
    message = message if message else "Values must not be blank"
    value = trim(value)
    if value:
        return value
    else:
        raise ValueError(message)


