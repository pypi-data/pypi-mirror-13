#!/usr/bin/python
# -*- coding: utf-8 -*-
# Scheduling interface library
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:

'''
Synchronous scheduler interface.  This implements a synchronous scheduler that
gets called periodically in a main loop function or just prior to commencing
other jobs.
'''

import time
import os
import threading
import six
import heapq
from sys import exc_info

from .base import TaskScheduler, ScheduledTask, NotExecutedYet

class SynchronousTaskScheduler(TaskScheduler):
    '''
    A synchronous task scheduler.  When polled, the scheduler checks
    for pending tasks and executes them.  Tasks are kept in a heap so that
    old tasks are executed first.
    '''

    def __init__(self):
        self._poll_lk = threading.Lock()
        self._pending_lk = threading.RLock()
        self._pending = []

    def _next(self):
        with self._pending_lk:
            if self._pending[0]._at_time > time.time():
                raise IndexError('Not yet pending')
            return heapq.heappop(self._pending)

    def _add(self, *tasks):
        with self._pending_lk:
            for t in tasks:
                heapq.heappush(self._pending, t)

    def poll(self):
        try:
            while True:
                task = self._next()
                if task.cancelled:
                    continue
                task.exec_task()
        except IndexError:
            pass

    def schedule(self, at_time, fn, *args, **kwargs):
        # Create a new task object.
        task = SynchronousScheduledTask(at_time, fn, args, kwargs)
        self._add(task)
        return task

    def cancel_all(self):
        pending = []
        with self._pending_lk:
            pending.extend(self._pending)
            self._pending = []
        for t in pending:
            if not t.cancelled:
                t.cancel()


class SynchronousScheduledTask(ScheduledTask):
    '''
    An implementation of a scheduled task executed synchronously.
    '''
    def __init__(self, at_time, fn, fn_args, fn_kwargs):
        self._at_time = at_time
        self._cancelled = False
        self._fn = fn
        self._fn_args = fn_args
        self._fn_kwargs = fn_kwargs
        self._fn_res = None
        self._fn_exc = None

    def _drop_fn(self):
        self._fn = None
        self._fn_args = None
        self._fn_kwargs = None

    def __lt__(self, other):
        '''
        Return true if this task's scheduled time is less than time of the
        one given.
        '''
        return self._at_time < other._at_time

    @property
    def cancelled(self):
        '''
        Returns true if the task has been cancelled.
        '''
        return self._cancelled

    def cancel(self):
        '''
        Cancel the scheduled task.
        '''
        if (not self.cancelled) and (self._fn is not None):
            self._cancelled = True
            self._drop_fn()

    @property
    def result(self):
        '''
        The result from the executed task.  Raises NotExecutedYet if not yet
        executed.
        '''
        if self.cancelled or (self._fn is not None):
            raise NotExecutedYet()

        if self._fn_exc is not None:
            six.reraise(*self._fn_exc)
        else:
            return self._fn_res

    def exec_task(self):
        try:
            self._fn_res = self._fn(*self._fn_args, **self._fn_kwargs)
        except:
            self._fn_exc = exc_info()
        self._drop_fn()
