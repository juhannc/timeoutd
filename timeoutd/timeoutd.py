"""Timeout decorator."""

from __future__ import annotations

import multiprocessing
import signal
import sys
import time
from functools import wraps
from typing import Callable


def _raise_exception(exception: type, exception_message: str | None):
    """This function checks if a exception message is given.

    If there is no exception message, the default behavior is
    maintained. If there is an exception message, the message is passed
    to the exception with the 'value' keyword.
    """
    if exception_message is None:
        raise exception()
    raise exception(exception_message)


def timeout(
    seconds: float | None = None,
    *,
    use_signals: bool = True,
    exception_type: type = TimeoutError,
    exception_message: str | None = None,
) -> Callable:
    """Add a timeout parameter to a function and return it.

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
    :param exception_type: optional exception to raise when the timeout
        is reached. If None is passed, the default behavior is to raise
        a TimeoutError exception.
    :type exception_type: type
    :param exception_message: optional message to pass to the exception
        when the timeout is reached.

    :raises: TimeoutError if time limit is reached

    It is illegal to pass anything other than a function as the first
    parameter. The function is wrapped and returned to the caller.
    """
    if not issubclass(exception_type, Exception):
        raise TypeError("exception_type must be a subclass of Exception")

    def decorate(function: Callable) -> Callable:
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

    return decorate


def _target(queue, function, *args, **kwargs) -> None:
    """Run a function with arguments and return output via a queue.

    This is a helper function for the Process created in _Timeout. It
    runs the function with positional arguments and keyword arguments
    and then returns the function's output by way of a queue. If an
    exception gets raised, it is returned to _Timeout to be raised by
    the value property.
    """
    try:
        queue.put((True, function(*args, **kwargs)))
    except Exception:  # pylint: disable=broad-except
        queue.put((False, sys.exc_info()[1]))


class _Timeout:  # pylint: disable=too-many-instance-attributes

    """Wrap a function and add a timeout (limit) attribute to it.

    Instances of this class are automatically generated by the
    add_timeout function defined above. Wrapping a function allows
    asynchronous calls to be made and termination of execution after a
    timeout has passed.
    """

    def __init__(
        self,
        function: Callable,
        on_timeout: Callable | None,
        exception_type: type,
        exception_message: str | None,
        limit: float | None,
    ):  # pylint: disable=too-many-arguments
        """Initialize instance in preparation for being called."""
        self.__limit = limit
        self.__function = function
        self.__exception_type = exception_type
        self.__exception_message = exception_message
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.__timeout = time.time()
        self.__process = multiprocessing.Process()
        self.__queue: multiprocessing.Queue = multiprocessing.Queue()

    def __call__(self, *args, **kwargs):
        """Execute the embedded function object asynchronously.

        The function given to the constructor is transparently called
        and requires that "ready" be intermittently polled. If and when
        it is True, the "value" property may then be checked for
        returned data.
        """
        self.__limit = kwargs.pop("timeout", self.__limit)
        self.__queue = multiprocessing.Queue(1)
        args = (self.__queue, self.__function) + args
        self.__process = multiprocessing.Process(
            target=_target, args=args, kwargs=kwargs
        )
        self.__process.daemon = True
        self.__process.start()
        if self.__limit is not None:
            self.__timeout = self.__limit + time.time()
        while not self.ready:
            time.sleep(0.01)
        return self.value

    def cancel(self):
        """Terminate any possible execution of the embedded function."""
        if self.__process.is_alive():
            self.__process.terminate()

        else:
            _raise_exception(self.__exception_type, self.__exception_message)

    @property
    def ready(self):
        """Read-only property indicating status of "value" property."""
        if self.__limit and self.__timeout < time.time():
            self.cancel()
        return self.__queue.full() and not self.__queue.empty()

    @property
    def value(self):
        """Read-only property containing data returned from function."""
        if self.ready is True:
            flag, load = self.__queue.get()
            if flag:
                return load
            raise load
        return None
