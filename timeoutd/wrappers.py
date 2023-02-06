"""This module contains the wrappers for the timeout decorator."""
from __future__ import annotations

import signal
from functools import wraps
from typing import Callable

from timeoutd._timeout import _Timeout
from timeoutd.exceptions import _raise_exception


def _signaler(
    function: Callable,
    seconds: float | None,
    use_signals: bool,
    exception_type: type,
    exception_message: str | None,
) -> Callable:
    """This function checks if signals should be used for timing out.

    If the use_signals flag is set to True, the signaler is used. If the
    flag is set to False, the multiprocessing is used.

    :param function: function to wrap
    :type function: Callable
    :param seconds: optional time limit in seconds or fractions of a
        second. If None is passed, no timeout is applied.
        This adds some flexibility to the usage: you can disable timing
        out depending on the settings.
    :type seconds: float
    :param use_signals: flag indicating whether signals should be used
        for timing function out or the multiprocessing.
        When using multiprocessing, timeout granularity is limited to
        10ths of a second.
    :type use_signals: bool
    :param exception_type: exception to raise when the timeout is
        reached.
    :type exception_type: type
    :param exception_message: optional message to pass to the exception
        when the timeout is reached.

    :return: wrapped function

    :raises: TimeoutError if time limit is reached.
    """
    if use_signals:

        def handler(*args, **kwargs):  # pylint: disable=unused-argument
            _raise_exception(exception_type, exception_message)

        @wraps(function)
        def new_function(*args, **kwargs):
            new_seconds = kwargs.pop("timeout", seconds)
            if new_seconds:
                old_handler = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, new_seconds)

            if not seconds:
                return function(*args, **kwargs)

            try:
                return function(*args, **kwargs)
            finally:
                if new_seconds:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    # reinstall the old signal handler
                    signal.signal(signal.SIGALRM, old_handler)

        return new_function

    @wraps(function)
    def new_mt_function(*args, **kwargs):
        timeout_wrapper = _Timeout(
            function=function,
            exception_type=exception_type,
            exception_message=exception_message,
            limit=seconds,
        )
        return timeout_wrapper(*args, **kwargs)

    return new_mt_function


def _exception_handler(
    function: Callable,
    on_timeout: Callable,
    *,
    exception_type: type,
    on_timeout_args: tuple | None,
    on_timeout_kwargs: dict | None,
) -> Callable:
    """This function catches the exception and calls the on_timeout function.

    :param function: function to wrap
    :type function: Callable
    :type on_timeout: Callable
    :param exception_type: optional exception to raise when the timeout
        is reached. If None is passed, the default behavior is to raise
        a TimeoutError exception.
    :type exception_type: type
    :param on_timeout_args: optional arguments to pass to the on_timeout
        function.
    :type on_timeout_args: tuple
    :param on_timeout_kwargs: optional keyword arguments to pass to the
        on_timeout function.
    :type on_timeout_kwargs: dict

    :return: wrapped function
    """
    if on_timeout_args is None:
        on_timeout_args = ()
    if on_timeout_kwargs is None:
        on_timeout_kwargs = {}

    @wraps(function)
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except exception_type:
            return on_timeout(*on_timeout_args, **on_timeout_kwargs)

    return new_function
