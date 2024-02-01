"""Timeout decorator tests."""

from datetime import datetime, timedelta

from timeoutd.converters import time_to_seconds


def test_converters_time_to_seconds_no_input():
    assert 0 == time_to_seconds()


def test_converters_time_to_seconds_only_limit_float():
    assert 5.05 == time_to_seconds(5.05)


def test_converters_time_to_seconds_only_limit_datetime():
    # Due to the delay from calling datetime.now() and comparing the
    # result, a small error might occur.
    assert 1 == round(time_to_seconds(datetime.now() + timedelta(seconds=1)), 4)


def test_converters_time_to_seconds_only_limit_timedelta():
    assert 7.12 == time_to_seconds(timedelta(seconds=7.12))


def test_converters_time_to_seconds_only_seconds():
    assert 4.2 == time_to_seconds(seconds=4.2)


def test_converters_time_to_seconds_only_minutes():
    assert 3 * 60 + 30 == time_to_seconds(minutes=3.5)


def test_converters_time_to_seconds_only_hours():
    assert 9 * 60 * 60 + 15 * 60 == time_to_seconds(hours=9.25)


def test_converters_time_to_seconds_seconds_and_minutes():
    assert 7.03 + 30 + 2 * 60 == time_to_seconds(seconds=7.03, minutes=2.5)


def test_converters_time_to_seconds_seconds_and_hours():
    assert 11.4 + 7.5 * 60 + 3 * 60 * 60 == time_to_seconds(seconds=11.4, hours=3.125)


def test_converters_time_to_seconds_minutes_and_hours():
    assert 15 + 3 * 60 + 45 * 60 + 1 * 60 * 60 == time_to_seconds(
        minutes=3.25, hours=1.75
    )
