# -*- coding: utf-8 -*-
import threading

__version__ = '1.0.7'
__license__ = 'MIT'
__author__ = 'pb'


import functools
import logging
from threading import Condition

class Delayer(object):
    current_timer = None
    condition = Condition()

    def __init__(self):
        pass

    @classmethod
    def _replace_current_task(cls, new_timer):
        with cls.condition:
            if cls.current_timer:
                try:
                    cls.current_timer.cancel()
                except ValueError:
                    logging.info("Task has already been finished")

            cls.current_timer = new_timer

    @classmethod
    def delay(cls, delay_time=5):

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kw):
                cls._replace_current_task(threading.Timer(delay_time, func, args, kw))
                cls.current_timer.start()
            return wrapper
        return decorator
