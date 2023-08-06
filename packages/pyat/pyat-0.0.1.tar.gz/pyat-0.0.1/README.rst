pyat
====

.. image:: https://travis-ci.org/vrtsystems/pyat.svg?branch=master
    :target: https://travis-ci.org/vrtsystems/pyat
.. image:: https://coveralls.io/repos/vrtsystems/pyat/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/vrtsystems/pyat?branch=master

`pyat` is the Python analogue of the Unix `at` daemon, it runs tasks at
specified times, optionally providing a means to pass around results and
exceptions.

The interface is intended to be able to support a variety of usage scenarios
including synchronous applications with a main loop, sporadically called
functions, multithreadded/multiprocessing based code and asynchronous frameworks
like Twisted or Tornado.

REQUIREMENTS
============

- `six`_

TYPICAL USAGE
=============

::

    import pyat.sync
    import time

    scheduler = pyat.sync.SynchronousScheduler()

    # ... etc ...

    background_task = None

    while True:
        # ... etc ...

        scheduler.poll()

        if foo == bar:
            # Do something in 10 seconds.
            background_task = scheduler.schedule(
                time.time() + 10, my_task, arg1, arg2, kwarg1=arg3)

        elif foo == baz:
            # Cancel task
            background_task.cancel()
            background_task = None

        elif (foo == quux) and (background_task is not None):
            # Check back on background task
            try:
                result = background_task.result
                # do something with result
                background_task = None
            except pyat.sync.NotExecutedYet:
                # A bit too early
                pass

STATUS
======

- Synchronous implementation `pyat.sync` works.

.. _`six`: https://pythonhosted.org/six/
