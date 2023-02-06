"""Timeout decorator."""

from __future__ import annotations

from typing import Callable

from timeoutd.wrappers import _exception_handler, _signaler


def timeout(
    seconds: float | None = None,
    on_timeout: Callable | None = None,
    *,
    use_signals: bool = True,
    exception_type: type = TimeoutError,
    exception_message: str | None = None,
    on_timeout_args: tuple | None = None,
    on_timeout_kwargs: dict | None = None,
) -> Callable:
    """Add a timeout parameter to a function and return it.

    :param seconds: optional time limit in seconds or fractions of a
        second. If None is passed, no timeout is applied.
        This adds some flexibility to the usage: you can disable timing
        out depending on the settings.
    :type seconds: float
    :param on_timeout: optional function to call when the timeout is
        reached instead of raising an exception. If None is passed,
        the default behavior is to raise a TimeoutError exception.
    :type on_timeout: Callable
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

    def decorate(function: Callable) -> Callable:
        if on_timeout is None:
            return _signaler(
                function,
                seconds=seconds,
                use_signals=use_signals,
                exception_type=exception_type,
                exception_message=exception_message,
            )
        return _exception_handler(
            _signaler(
                function,
                seconds=seconds,
                use_signals=use_signals,
                exception_type=exception_type,
                exception_message=exception_message,
            ),
            on_timeout=on_timeout,
            exception_type=exception_type,
            on_timeout_args=on_timeout_args,
            on_timeout_kwargs=on_timeout_kwargs,
        )

    return decorate
