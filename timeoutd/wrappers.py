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
) -> Callable:
    @wraps(function)
    def new_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except exception_type:
            return on_timeout()

    return new_function
