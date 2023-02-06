"""This module contains the exception thrower."""
from __future__ import annotations


def _raise_exception(exception: type, exception_message: str | None):
    """This function checks if a exception message is given.

    If there is no exception message, the default behavior is
    maintained. If there is an exception message, the message is passed
    to the exception with the 'value' keyword.
    """
    if exception_message is None:
        raise exception()
    raise exception(exception_message)
