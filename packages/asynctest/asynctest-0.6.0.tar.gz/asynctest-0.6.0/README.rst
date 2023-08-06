=========
asynctest
=========

The package asynctest is built on top of the standard unittest module and
cuts down boilerplate code when testing libraries for asyncio.

Currently, asynctest targets the "selector" model, hence, some features
will not (yet?) work with Windows' proactor.

Author & license
----------------

Authored by Martin Richard <martius@martiusweb.net> and licensed under the
Apache 2 license.

Documentation
-------------

.. image:: https://readthedocs.org/projects/asynctest/badge/
   :target: http://asynctest.readthedocs.org/en/latest/

Full documentation is available at http://asynctest.readthedocs.org/en/latest/,

Features
--------

TestCase and FunctionTestCase
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Initialize and close a loop created for each test, if the loop uses
    a selector, it will be updated with a TestSelector object wrapping the
    original selector (see below),
  - if the test function is a coroutine function or returns a coroutine, it
    will run on the loop,
  - TestCase.setUp() and TestCase.tearDown() can be coroutine functions,
  - a test fails if the loop did not run during the test.


Mock and CoroutineMock
~~~~~~~~~~~~~~~~~~~~~~

  - CoroutineMock is a new Mock class which mocks a coroutine function, and
    returns a coroutine when called,

  - NonCallableMock, Mock and CoroutineMock can return CoroutineMock objects
    when its attributes are get if there is a matching attribute in the spec
    (or spec_set) object which is a coroutine function,

  - patch(), patch.object(), patch.multiple() return a MagickMock or
    CoroutineMock object by default, according to the patched target,

  - patch(), patch.object(), patch.multiple() handle generators and coroutines,

  - all the patch() methods can decorate coroutine functions,

  - mock_open() returns a MagickMock object by default.

  - return_once() can be used with Mock.side_effect to return a value only
    once when a mock is called.


Selectors
~~~~~~~~~

The module asynctest.selector provides classes to mock objects performing IO
(files, sockets, etc).

  - FileMock is a special type of mock which represents a file.
    FileMock.fileno() returns a special value which allows to identify uniquely
    the mock,

  - SocketMock is a special type of FileMock which uses socket.socket as spec,

  - TestSelector is a custom selector able to wrap a real selector
    implementation and deal with FileMock objects, it can replace a selector
    loop by calling `loop._selector = TestSelector(loop._selector)`, and will
    intercept mock so they don't get registered to the actual selector.

  - set_read_ready() and set_write_ready() to force read and write event
    callbacks to be scheduled on the loop, as if the selector scheduled them.

Helpers
~~~~~~~

  - the coroutine exhaust_callbacks(loop) returns once all the callbacks which
    should be called immediatly are executed, which is useful when the test
    author needs to assert things which are not yet executed by the loop.

Roadmap
-------

I hope I will find time to develop and release the following features:

- set of warnings against common mistakes (0.7 ?)
- proactor support (0.8 ?)

Tests
-----

asynctest is unit tested. You can run asynctest test suite with this command:

::

$ PYTHONPATH=. python -m unittest test
