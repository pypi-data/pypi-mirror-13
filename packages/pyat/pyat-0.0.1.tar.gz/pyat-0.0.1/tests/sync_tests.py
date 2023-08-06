# -*- coding: utf-8 -*-
# Scheduling interface library
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:

import pyat.sync
import time
import random

from .util import a_task, a_failing_task, make_args, make_kwargs, \
        FailedTaskException

MIN_TIME = 1.0
MAX_TIME = 2.0
DELTA_TIME = MAX_TIME - MIN_TIME
STEP_TIME = 0.1
TIMEOUT_DELAY = 0.5


def test_future():
    '''
    Test a task scheduled N seconds in the future is executed close to the
    requested time.
    '''
    # Create scheduler
    scheduler = pyat.sync.SynchronousTaskScheduler()

    # Pick some random arguments
    args = make_args()
    kwargs = make_kwargs()

    # Pick a time between 1-5 seconds in the future
    delay = MIN_TIME + (random.random() * DELTA_TIME)
    at_time = time.time() + delay

    # Schedule task
    task = scheduler.schedule(at_time, a_task, *args, **kwargs)

    # Pick a timeout
    timeout = at_time + TIMEOUT_DELAY

    # Wait for timeout
    while time.time() < timeout:
        time.sleep(STEP_TIME)
        scheduler.poll()

    # Did our function get run?
    try:
        (run_at, run_args, run_kwargs) = task.result
        assert run_args == args, 'args does not match'
        assert run_kwargs == kwargs, 'kwargs does not match'
        assert run_at > at_time, 'Ran too early'
        assert run_at < (at_time + STEP_TIME), 'Ran too late'
    except pyat.sync.NotExecutedYet:
        assert False, 'Did not get executed'


def test_future_exception():
    '''
    Test a task scheduled N seconds in the future that fails.
    '''
    # Create scheduler
    scheduler = pyat.sync.SynchronousTaskScheduler()

    # Pick some random arguments
    args = make_args()
    kwargs = make_kwargs()

    # Pick a time between 1-5 seconds in the future
    delay = MIN_TIME + (random.random() * DELTA_TIME)
    at_time = time.time() + delay

    # Schedule task
    task = scheduler.schedule(at_time, a_failing_task, *args, **kwargs)

    # Pick a timeout
    timeout = at_time + TIMEOUT_DELAY

    # Wait for timeout
    while time.time() < timeout:
        time.sleep(STEP_TIME)
        scheduler.poll()

    # Did our function get run?
    try:
        (run_at, run_args, run_kwargs) = task.result
        assert False, 'Did not fail'
    except FailedTaskException as e:
        (msg, run_at, run_args, run_kwargs) = e.args
        assert run_args == args, 'args does not match'
        assert run_kwargs == kwargs, 'kwargs does not match'
        assert run_at > at_time, 'Ran too early'
        assert run_at < (at_time + STEP_TIME), 'Ran too late'
    except pyat.sync.NotExecutedYet:
        assert False, 'Did not get executed'


def test_future_cancelled():
    '''
    Test a task scheduled N seconds in the future then cancelled doesn't
    execute.
    '''
    # Create scheduler
    scheduler = pyat.sync.SynchronousTaskScheduler()

    # Pick some random arguments
    args = make_args()
    kwargs = make_kwargs()

    # Pick a time between 1-5 seconds in the future
    delay = MIN_TIME + (random.random() * DELTA_TIME)
    at_time = time.time() + delay

    # Schedule task
    task = scheduler.schedule(at_time, a_task, *args, **kwargs)

    # Poll once
    scheduler.poll()

    # Cancel the task
    task.cancel()
    assert task.cancelled, 'Not cancelled'

    # Pick a timeout
    timeout = at_time + TIMEOUT_DELAY

    # Wait for timeout
    while time.time() < timeout:
        time.sleep(STEP_TIME)
        scheduler.poll()

    # Did our function get run?
    try:
        (run_at, run_args, run_kwargs) = task.result
        assert False, 'Task executed'
    except pyat.sync.NotExecutedYet:
        pass


def test_cancel_all():
    '''
    Test we can cancel all tasks.
    '''
    # Create scheduler
    scheduler = pyat.sync.SynchronousTaskScheduler()

    # Pick some random arguments
    args = make_args()
    kwargs = make_kwargs()

    # Pick a time between 1-5 seconds in the future
    delay = MIN_TIME + (random.random() * DELTA_TIME)
    at_time = time.time() + delay

    # Schedule tasks
    task1 = scheduler.schedule(at_time, a_task, *args, **kwargs)
    task2 = scheduler.schedule(at_time + 1, a_task, *args, **kwargs)
    task3 = scheduler.schedule(at_time + 2, a_task, *args, **kwargs)

    # Poll once
    scheduler.poll()

    # Cancel all tasks
    scheduler.cancel_all()

    # Pick a timeout
    timeout = at_time + TIMEOUT_DELAY

    # Wait for timeout
    while time.time() < timeout:
        time.sleep(STEP_TIME)
        scheduler.poll()

    # Did our functions get run?
    for task in (task1, task2, task3):
        try:
            (run_at, run_args, run_kwargs) = task.result
            assert False, 'Task executed'
        except pyat.sync.NotExecutedYet:
            pass


def test_not_yet_executed():
    '''
    Test NotYetExecuted gets raised if we ask the task early.
    '''
    # Create scheduler
    scheduler = pyat.sync.SynchronousTaskScheduler()

    # Pick some random arguments
    args = make_args()
    kwargs = make_kwargs()

    # Pick a time between 1-5 seconds in the future
    delay = MIN_TIME + (random.random() * DELTA_TIME)
    at_time = time.time() + delay

    # Schedule task
    task = scheduler.schedule(at_time, a_task, *args, **kwargs)

    # Poll once
    scheduler.poll()

    # Did our function get run?
    try:
        (run_at, run_args, run_kwargs) = task.result
        assert False, 'Task executed early'
    except pyat.sync.NotExecutedYet:
        pass
