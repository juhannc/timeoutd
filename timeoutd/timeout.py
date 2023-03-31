"""Timeout decorator."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from timeoutd.converters import time_to_seconds
from timeoutd.handlers import exception_handler, retry_handler, timeout_handler


def timeout(
    limit: float | datetime | timedelta | None = None,
    *,
    seconds: float | None = None,
    minutes: float | None = None,
    hours: float | None = None,
    on_timeout: Callable | None = None,
    retries: int | None = None,
    use_signals: bool = True,
    exception_type: type = TimeoutError,
    exception_message: str | None = None,
    on_timeout_args: tuple | None = None,
    on_timeout_kwargs: dict | None = None,
) -> Callable:
    """Add a timeout parameter to a function and return it.

    :param limit: optional time limit in either seconds (or fractions of
        it) or a datetime object with a specified timeout date. If one
        wants to specify a timeout in minutes, hours, and seconds, the
        seconds, minutes, and hours parameters can be used.
        If neither is passed, no timeout is applied but if both a limit
        and a set of hours, minutes, and seconds is provided, the limit
        will be used.
        This adds some flexibility to the usage: you can disable timing
        out depending on the settings.
    :type limit: float | datetime | None
    :param on_timeout: optional function to call when the timeout is
        reached instead of raising an exception. If None is passed,
        the default behavior is to raise a TimeoutError exception.
    :type on_timeout: Callable | None
    :param retries: optional number of retries to perform when the
        timeout is reached. If None is passed, the default behavior is
        to not retry. If a number is passed, the function will be
        retried that number of times. If the function is retried, the
        timeout will be reset for each retry. If retry is set to values
        greater than 0 but no `on_timeout` function is provided, the
        default behavior is to retry the decorated function.
    :type retries: int | None
    :param seconds: optional time limit in seconds or fractions of a
        second. See the `limit` parameter for more information.
    :type seconds: float | None
    :param minutes: optional time limit in minutes or fractions of a
        minute. See the `limit` parameter for more information.
    :type minutes: float | None
    :param hours: optional time limit in hours or fractions of an hour.
        See the `limit` parameter for more information.
    :type hours: float | None
    :param use_signals: flag indicating whether signals should be used
        for timing function out or the multiprocessing.
        When using multiprocessing, timeout granularity is limited to
        10ths of a second.
    :type use_signals: bool
    :param exception_type: optional exception to raise when the timeout
        is reached. If None is passed, the default behavior is to raise
        a TimeoutError exception.
    :type exception_type: type
    :param exception_message: optional message to pass to the exception
        when the timeout is reached.
    :param on_timeout_args: optional arguments to pass to the on_timeout
        function.
    :type on_timeout_args: tuple
    :param on_timeout_kwargs: optional keyword arguments to pass to the
        on_timeout function.
    :type on_timeout_kwargs: dict

    :return: wrapped function

    :raises: TimeoutError if time limit is reached

    It is illegal to pass anything other than a function as the first
    parameter. The function is wrapped and returned to the caller.
    """
    if not issubclass(exception_type, Exception):
        raise TypeError("exception_type must be a subclass of Exception")

    seconds = time_to_seconds(
        limit=limit, seconds=seconds, minutes=minutes, hours=hours
    )

    _retries = retries if retries is not None else 0
    if _retries < 0:
        raise ValueError("retries must be greater than or equal to 0")
    if not isinstance(_retries, int):
        raise TypeError("retries must be an integer")

    def decorate(function: Callable) -> Callable:
        """Decorate a function with a timeout."""
        handled_timeout = timeout_handler(
            function,
            seconds=seconds,
            use_signals=use_signals,
            exception_type=exception_type,
            exception_message=exception_message,
        )

        if _retries == 0:
            if on_timeout is None:
                return handled_timeout
            return exception_handler(
                handled_timeout,
                on_timeout=on_timeout,
                exception_type=exception_type,
                on_timeout_args=on_timeout_args,
                on_timeout_kwargs=on_timeout_kwargs,
            )

        if on_timeout is None:
            return retry_handler(
                exception_handler(
                    handled_timeout,
                    on_timeout=handled_timeout,
                    exception_type=exception_type,
                    on_timeout_args=on_timeout_args,
                    on_timeout_kwargs=on_timeout_kwargs,
                ),
                retries=_retries,
            )
        return retry_handler(
            exception_handler(
                handled_timeout,
                on_timeout=on_timeout,
                exception_type=exception_type,
                on_timeout_args=on_timeout_args,
                on_timeout_kwargs=on_timeout_kwargs,
            ),
            retries=_retries,
        )

    return decorate
