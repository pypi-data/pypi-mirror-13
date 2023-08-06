#!/usr/bin/python
# -*- coding: utf-8 -*-
# Scheduling interface library
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:


class TaskScheduler(object):  # pragma: no cover
    '''
    This is a simple interface for scheduling a task to execute at some point
    in the future.  This is an abstract class.
    '''

    def poll(self):
        '''
        Poll the scheduler.  This executes any tasks due to be executed.

        Subclasses that have other ways to ensure execution takes place may
        make this function a no-op.
        '''
        raise NotImplementedError()

    def schedule(self, at_time, fn, *args, **kwargs):
        '''
        Schedule at the time given by `at_time`, a call of the function "fn".
        '''
        raise NotImplementedError()

    def cancel_all(self):
        '''
        Cancel all pending tasks.
        '''
        raise NotImplementedError()


class ScheduledTask(object):  # pragma: no cover
    '''
    This is an object returned by the task scheduler to represent the task
    that was scheduled.  This is an abstract class.
    '''

    def cancel(self):
        '''
        Cancel the scheduled task.
        '''
        raise NotImplementedError()

    @property
    def cancelled(self):
        '''
        Returns true if the task has been cancelled.
        '''
        raise NotImplementedError()

    @property
    def result(self):
        '''
        The result from the executed task.  Raises NotExecutedYet if not yet
        executed.
        '''
        raise NotImplementedError()


class NotExecutedYet(Exception):
    '''
    Exception raised when .result is called on a task that hasn't been run yet.
    '''
    pass
