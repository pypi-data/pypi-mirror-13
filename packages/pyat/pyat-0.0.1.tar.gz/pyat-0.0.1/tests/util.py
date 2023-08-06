# -*- coding: utf-8 -*-
# Scheduling interface library
# (C) 2016 VRT Systems
#
# vim: set ts=4 sts=4 et tw=78 sw=4:

import random
import time

def a_task(*args, **kwargs):
    '''
    A task that returns the arguments it was given along with the time
    it was executed.
    '''
    return (time.time(), args, kwargs)

def a_failing_task(*args, **kwargs):
    '''
    A task that raises an exception.
    '''
    raise FailedTaskException('I failed', time.time(), args, kwargs)

class FailedTaskException(Exception):
    pass


def random_value():
    '''
    Generate a ramdomised scalar value to use as an argument.
    '''
    t = random.choice(['int', 'str', 'bool'])
    if t == 'int':
        # Make it a numeric argument
        return random.randint(-1000,1000)
    elif t == 'str':
        # Make it a string argument
        return 'str:%f' % random.random()
    elif t == 'bool':
        # Make it a bool.
        return (random.random() > 0.5)

def make_args():
    # Pick some random arguments
    return tuple(map(lambda n : random_value(), range(random.randint(0,10))))

def make_kwargs():
    kwargs = {}
    for n in range(random.randint(0,10)):
        arg = 'arg%d' % n
        kwargs[arg] = random_value()
    return kwargs
