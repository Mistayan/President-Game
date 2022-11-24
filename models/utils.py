# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/19/22
Imported from : https://www.freecodecamp.org/news/python-decorators-explained-with-examples/
"""
import json
import tracemalloc
from abc import ABC
from functools import wraps
from time import perf_counter

from models import root_logger


class SerializableObject(object):

    def __init__(self, *arg, **kwargs):
        pass

    def to_json(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__ if not isinstance(o,
                                                                                          ABC) else o.__repr__(),
                                     sort_keys=True, indent=4,
                                     check_circular=True, ensure_ascii=False, allow_nan=True))


class SerializableClass(object):

    def __init__(self):
        pass

    def to_json(self):
        public_names = [d for d in self.__dir__()
                        if str(d)[0] != '_' and str(d) not in ("to_json", "ROUTES")]
        public_attributes = [self.__getattribute__(a) for a in public_names]
        _T_dict = {public_names[i]: public_attributes[i] for i in range(len(public_names))}
        root_logger.debug(_T_dict)
        return json.loads(json.dumps(_T_dict))


class ValidateBuffer:
    """
    On method call, verify buffer content (headers, requirements, tokens, ...)
    """

    def __init__(self, message_before: str = None, message_after: str = ""):
        self.before = message_before
        self.after = message_after
        self.__buffer = None

    def __call__(self, f):
        def validate(*args, **kwargs):
            self.__buffer = kwargs
            print(f"Buffer validation ==> {f}({args}\t{kwargs})")
            if not (args or kwargs):
                raise BufferError("Nothing to apply. Empty buffer")
            response = f(*args, **kwargs)
            self.after and root_logger.debug(f"{self.after}")
            return response

        self.before and root_logger.debug(f"{self.before}")
        return validate


def measure_performance(func):
    """Measure performance of a function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = perf_counter()
        func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        finish_time = perf_counter()
        print(f'Function: {func.__name__}')
        print(f'Method: {func.__doc__}')
        print(f'Memory usage:\t\t {current / 10 ** 6:.6f} MB \n'
              f'Peak memory usage:\t {peak / 10 ** 6:.6f} MB ')
        print(f'Time elapsed is seconds: {finish_time - start_time:.6f}')
        print(f'{"-" * 40}')
        tracemalloc.stop()

    return wrapper
