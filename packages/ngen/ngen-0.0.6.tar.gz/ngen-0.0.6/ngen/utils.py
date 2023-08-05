from functools import wraps
from twisted.internet import reactor

import time


DEFAULT_PATH = '_tmp.log'


def threaded(func):
    """
        method decorator that will run the wrapped function in a thread
        managed by twisted's reactor
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        reactor.callInThread(func, self, *args, **kwargs)
    return wrapper


def simple_timer(func):
    """
        a simple decorator that can be used to wrap a given function in order
        to record how much time it took to complete the execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        finish = time.time()
        delta = finish - start
        with open(DEFAULT_PATH, 'a') as _file:
            _file.write(
                'simple_timer: "%s" took %fs to complete.\n' % (
                    func.__name__, delta
                )
            )
        return ret
    return wrapper


class TimerContext(object):
    """
        a context manager that can be used to record the time taken to execute
        a sequence of functions.
    """
    start = None
    finish = None
    delta = None

    def __init__(self, path=None, name=None):
        self.path = path or DEFAULT_PATH
        self.name = name or 'None'

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, tracebk):
        self.finish = time.time()
        self.delta = self.finish - self.start
        with open(self.path, 'a') as _file:
            _file.write(
                'TimerContext: "%s" took %fs to complete.\n' % (
                    self.name, self.delta
                )
            )


def timer(path=None):
    """
        a decorator that can be used to track time taken to execute the
        wrapped function, it accepts a path argument.
    """
    _path = path or DEFAULT_PATH

    def _timer(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            finish = time.time()
            delta = finish - start
            with open(_path, 'a') as _file:
                _file.write(
                    'timer: "%s" took %fs to complete.\n' % (
                        func.__name__, delta
                    )
                )
            return ret
        return wrapper
    return _timer


# ripped from Django
class cached_property(object):
    """
        Decorator that converts a method with a single self argument into a
        property cached on the instance.

        Optional ``name`` argument allows you to make cached properties of
        other methods.
        (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


def chunk(array, size, strict=False):
    last = None if not strict else len(array) / size
    return [
        array[idx:idx + size]
        for idx in xrange(0, len(array), size)
    ][:last]
