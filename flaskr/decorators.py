"""Decorators"""
from threading import Thread


def asynchronous(f):
    """Threading for asynchronous sending."""
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
