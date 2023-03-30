# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/19/22
Imported from : https://www.freecodecamp.org/news/python-decorators-explained-with-examples/
"""
import asyncio
import json
import socket
import tracemalloc
from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from conf import ROOT_LOGGER

logger = ROOT_LOGGER.getChild(__name__)


class SerializableObject(ABC):
    """
    Base abstract class to serialize an object.

    !!! COMMUNICATION / SECURITY WARNING !!!
    If an object inherit from this class, please ensure that returned values given by to_json()
    are filtered to not expose sensitive datas.

    This class method is only supposed to be used for the sake of __PUBLIC messages__
    (in this project at least)
    """

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """ Just instantiate methods """
        super().__init__(*args, **kwargs)

    def to_json(self):
        """
        Collect any possible values given by to_json() from children and supers

        Override __dict__, to customize what your object should return

       SECURITY WARNING :
        - This method is used for communications as public messages in this project

        - If object is used for communications, ensure no sensitive data are exposed publicly

        - If subclass is abstract, ensure __repr__() is defined
        """
        return json.loads(json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True, indent=4,
            check_circular=True, ensure_ascii=False, allow_nan=True)
        )


class SerializableClass:
    """Serializes an instantiated class to JSON easily. Clazz(SerializableClass)"""

    def __init__(self):
        """Enforce init method on class"""

    def to_json(self):
        """ find every public data in class and returns it as json_dict """
        public_names = [d for d in dir(self)
                        if str(d)[0] != '_' and str(d) not in ("to_json", "ROUTES")]
        public_attributes = [getattr(self, a) for a in public_names]
        any_type_dict = {public_names[i]: public_attributes[i] for i in range(len(public_names))}
        ROOT_LOGGER.debug(any_type_dict)
        return json.loads(json.dumps(any_type_dict))


class ValidateBuffer:
    """
    On method call, verify buffer content (headers, requirements, tokens, ...)
    """

    def __init__(self, message_before: str = None, message_after: str = ""):
        """
        Wrapper class to validate information given to a method or a class
        :param message_before: message to show before running method/class
        :param message_before: message to show after running method/class
        """
        self.before = message_before
        self.after = message_after
        self.__buffer = None

    def __call__(self, fn):
        """ whenever this class is called (instantiated or not) execute buffer validation """

        def validate(*args, **kwargs):
            """ Validate that method/class received arguments to process """
            self.__buffer = kwargs
            print(f"Buffer validation ==> {fn}({args}\t{kwargs})")
            if not (args or kwargs):
                raise BufferError("Nothing to apply. Empty buffer")
            response = fn(*args, **kwargs)
            ROOT_LOGGER.debug(self.after) if self.after else None
            return response

        ROOT_LOGGER.debug(self.before) if self.before else None
        return validate


def measure_perf(func):
    """Measure performance of a function/method/class"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """ wrapper is like the function it-self. Requires to run the function/method/class in here"""
        tracemalloc.start()
        timeit = perf_counter()
        return_value = func(*args, **kwargs)
        total_time = perf_counter() - timeit
        current, peak = tracemalloc.get_traced_memory()
        logger.debug(f'Function: {func.__name__}')
        logger.debug(f'Method: {func.__doc__}')
        logger.debug(f'Memory usage:\t\t {current / 10 ** 6:.6f} MB \n'
                     f'Peak memory usage:\t {peak / 10 ** 6:.6f} MB ')
        logger.debug(f'Time elapsed is seconds: {total_time:.6f}')
        logger.debug(f'{"-" * 40}')
        tracemalloc.stop()
        return return_value
    return wrapper


async def async_range(min_, max_, iter_=1):
    for i in range(min_, max_, iter_):
        yield i
        await asyncio.sleep(0.0)


class GameFinder:
    """
    A class that allows us to find running game and interface servers
    to create a new server, use availabilities,
    to join a server, use running servers
    """

    def __init__(self, **kwargs):
        """ Instantiate the GameFinder
        :param kwargs:  - target    : the target server (localhost, ...)
                        - range     : port(s) to scan on the given target
        Stores target:port available/running game servers
        """
        target = kwargs.get("target", "localhost")
        _range = kwargs.get("range", range(5001, 5012))
        if isinstance(_range, tuple):
            _range = range(_range[0] + 1, _range[1] + 1)
        elif isinstance(_range, int):
            _range = range(_range + 1, _range + 2)
        self.running = asyncio.run(scan_ports_availabilities(target, _range))
        logger.debug(self.running)
        self.availabilities = [(target, port) for port in _range if (target, port) not in self.running]
        logger.debug(self.availabilities)


async def scan_ports_availabilities(target="localhost", range=range(5002, 5012)) -> list:
    """ Scan ports availability on given target """

    async def scan_port(_port):
        """ Scan port availability on given target """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)

            # returns an error indicator
            result = sock.connect_ex((target, _port))
            sock.close()
            if result == 0:
                return _port
        except:
            pass

    tasks = []
    for port in range:
        tasks.append(asyncio.create_task(scan_port(port)))
    done, _ = await asyncio.wait(tasks)
    return [(target, task.result()) for task in done if task.result()]
