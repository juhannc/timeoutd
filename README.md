# timeoutd

![pytest](https://github.com/juhannc/timeoutd/actions/workflows/pytest.yml/badge.svg)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/juhannc/timeoutd/main.svg)](https://results.pre-commit.ci/latest/github/juhannc/timeoutd/main)
[![codecov](https://codecov.io/gh/juhannc/timeoutd/branch/main/graph/badge.svg)](https://codecov.io/gh/juhannc/timeoutd)
[![Maintainability](https://api.codeclimate.com/v1/badges/ba14c01e22ad0343af8c/maintainability)](https://codeclimate.com/github/juhannc/timeoutd/maintainability)

[![Pypi Status](https://badge.fury.io/py/timeoutd.svg)](https://badge.fury.io/py/timeoutd)

## Installation

From [PyPI](https://pypi.org/project/timeoutd/):

```shell
pip install timeoutd
```

From source code:

```shell
git clone https://github.com/juhannc/timeoutd.git
pip install -e .
```

## Usage

The `timeoutd` module provides a decorator that can be used to limit the execution time of a function.
The decorator takes a single argument, the number of seconds or a specific date (as a datetime object) after which the function should be terminated.

```python
import time

import timeoutd

@timeoutd.timeout(5)
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()
```

The `timeout` decorator allows for multiple different ways to specify the timeout, for example with a datetime object:

```python
import time
import datetime

import timeoutd

@timeoutd.timeout(datetime.datetime.now() + datetime.timedelta(0, 5))
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()
```

It also take a `timedelta` object:

```python
import time
import datetime

import timeoutd

@timeoutd.timeout(datetime.timedelta(0, 5))
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()
```

But it can also take a delta in form of hours, minutes, and seconds via the kwargs:

```python
import time

import timeoutd

@timeoutd.timeout(hours=0, minutes=0, seconds=5)
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()
```

The `timeout` decorator also accepts a custom exception to raise on timeout:

```python
import time

import timeoutd

@timeoutd.timeout(5, exception_type=StopIteration)
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()

```

You can also specify a function to be called on timeout instead of raising an exception:

```python
import time

import timeoutd

def add_two_numbers(i: int, j: int | None = None):
    if j is None:
        j = 0
    print(f"The sum of {i = } and {j = } is {i + j}")

@timeoutd.timeout(
    5,
    on_timeout=add_two_numbers,
    on_timeout_args=(1,),
    on_timeout_kwargs={"j": 2}
)
def mytest():
    print("Start")
    for i in range(1, 10):
        time.sleep(1)
        print(f"{i} seconds have passed")

if __name__ == '__main__':
    mytest()
```

### Multithreading

_Note:_ This feature appears to be broken in some cases for the original timeout-decorator.
Some issues might still exist in this fork.

By default, `timeoutd` uses signals to limit the execution time of the given function.
This approach does not work if your function is executed not in a main thread (for example if it's a worker thread of the web application).
There is alternative timeout strategy for this case - by using multiprocessing.
To use it, just pass `use_signals=False` to the timeout decorator function:

```python
import time

import timeoutd

@timeoutd.timeout(5, use_signals=False)
def mytest():
    print "Start"
    for i in range(1, 10):
        time.sleep(1)
        print("{} seconds have passed".format(i))

if __name__ == '__main__':
    mytest()
```

_Warning:_
Make sure that in case of multiprocessing strategy for timeout, your function does not return objects which cannot be pickled, otherwise it will fail at marshalling it between master and child processes.

## Acknowledgement

Derived from
<http://www.saltycrane.com/blog/2010/04/using-python-timeout-decorator-uploading-s3/>, <https://code.google.com/p/verse-quiz/source/browse/trunk/timeout.py>, and <https://github.com/pnpnpn/timeout-decorator>
