"""Timeout decorator tests."""
import time

import pytest

from timeoutd import timeout

TIMEOUT = 0.1
EXCEPTION_MESSAGE = "Timeout exceeded."


@pytest.fixture(params=[False, True])
def use_signals(request):
    """Use signals for timing out or not."""
    return request.param


def test_timeout_decorator_arg(use_signals):
    @timeout(seconds=TIMEOUT, use_signals=use_signals)
    def f():
        time.sleep(2)

    with pytest.raises(TimeoutError):
        f()


def test_timeout_class_method(use_signals):
    class c:
        @timeout(seconds=TIMEOUT, use_signals=use_signals)
        def f(self):
            time.sleep(2)

    with pytest.raises(TimeoutError):
        c().f()


def test_timeout_kwargs(use_signals):
    @timeout(seconds=0.3, use_signals=use_signals)
    def f():
        time.sleep(0.2)

    with pytest.raises(TimeoutError):
        f(timeout=0.1)


def test_timeout_alternate_exception(use_signals):
    @timeout(seconds=0.3, use_signals=use_signals, exception_type=StopIteration)
    def f():
        time.sleep(0.2)

    with pytest.raises(StopIteration):
        f(timeout=0.1)


def test_timeout_kwargs_with_initial_timeout_none(use_signals):
    @timeout(use_signals=use_signals)
    def f():
        time.sleep(0.2)

    with pytest.raises(TimeoutError):
        f(timeout=0.1)


def test_timeout_no_seconds(use_signals):
    @timeout(use_signals=use_signals)
    def f():
        time.sleep(0.1)

    f()


def test_timeout_partial_seconds(use_signals):
    @timeout(seconds=0.2, use_signals=use_signals)
    def f():
        time.sleep(0.5)

    with pytest.raises(TimeoutError):
        f()


def test_timeout_ok(use_signals):
    @timeout(seconds=0.2, use_signals=use_signals)
    def f():
        time.sleep(0.1)

    f()


def test_function_name(use_signals):
    @timeout(seconds=0.2, use_signals=use_signals)
    def func_name():
        pass

    assert func_name.__name__ == "func_name"


def test_timeout_custom_on_timeout(use_signals):
    def on_timeout():
        return 0

    @timeout(seconds=TIMEOUT, on_timeout=on_timeout, use_signals=use_signals)
    def f():
        time.sleep(2)

    assert f() == 0


def test_timeout_custom_on_timeout_with_args(use_signals):
    def on_timeout(i, j):
        return i + j

    @timeout(
        seconds=TIMEOUT,
        on_timeout=on_timeout,
        use_signals=use_signals,
        on_timeout_args=(1, 2),
    )
    def f():
        time.sleep(2)

    assert f() == 3


def test_timeout_custom_on_timeout_with_kwargs(use_signals):
    def on_timeout(i=0, j=1):
        return i + j

    @timeout(
        seconds=TIMEOUT,
        on_timeout=on_timeout,
        use_signals=use_signals,
        on_timeout_kwargs={"i": 1, "j": 2},
    )
    def f():
        time.sleep(2)

    assert f() == 3


def test_timeout_custom_on_timeout_with_args_and_kwargs(use_signals):
    def on_timeout(i, j=1):
        return i + j

    @timeout(
        seconds=TIMEOUT,
        on_timeout=on_timeout,
        use_signals=use_signals,
        on_timeout_args=(1,),
        on_timeout_kwargs={"j": 2},
    )
    def f():
        time.sleep(2)

    assert f() == 3


def test_timeout_pickle_error():
    """Test that when a pickle error occurs a timeout error is raised."""

    @timeout(seconds=TIMEOUT, use_signals=False)
    def f():
        time.sleep(0.1)

        class Test:
            pass

        return Test()

    with pytest.raises(TimeoutError):
        f()


def test_timeout_custom_exception_message():
    @timeout(seconds=TIMEOUT, exception_message=EXCEPTION_MESSAGE)
    def f():
        time.sleep(2)

    with pytest.raises(TimeoutError, match=EXCEPTION_MESSAGE):
        f()


def test_timeout_custom_exception_with_message():
    @timeout(
        seconds=TIMEOUT,
        exception_type=RuntimeError,
        exception_message=EXCEPTION_MESSAGE,
    )
    def f():
        time.sleep(2)

    with pytest.raises(RuntimeError, match=EXCEPTION_MESSAGE):
        f()


def test_timeout_exception_is_of_wrong_type():
    with pytest.raises(TypeError):

        @timeout(seconds=TIMEOUT, exception_type=str)
        def f():
            time.sleep(2)
