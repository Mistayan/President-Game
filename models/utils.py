# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/19/22
Imported from : https://www.freecodecamp.org/news/python-decorators-explained-with-examples/
"""
import json
import socket
import tracemalloc
from abc import ABC, abstractmethod
from functools import wraps
from time import perf_counter

from models import ROOT_LOGGER


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


class SerializableClass(object):

    def __init__(self):
        pass

    def to_json(self):
        public_names = [d for d in self.__dir__()
                        if str(d)[0] != '_' and str(d) not in ("to_json", "ROUTES")]
        public_attributes = [self.__getattribute__(a) for a in public_names]
        _T_dict = {public_names[i]: public_attributes[i] for i in range(len(public_names))}
        ROOT_LOGGER.debug(_T_dict)
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
            self.after and ROOT_LOGGER.debug(f"{self.after}")
            return response

        self.before and ROOT_LOGGER.debug(f"{self.before}")
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


class GameFinder:
    """
    A class that allow us to find running game and interfaces servers
    to create a new server, use availabilities,
    to join a server, use running servers
    """

    def __init__(self, **kwargs):
        self.availabilities = []
        self.running_servers = []
        self.target = kwargs.get("target", "localhost")

        # Kwargs parsing
        range_min, range_max = kwargs.get("range", (0, 0))  # TODO str = 'A'
        port = kwargs.get("port", 0)
        if range_min and range_max: 
            self.range = range(range_min+1, range_max+1)
        elif port:
            self.range = (port+1, port+1)
        else:
            self.range = (5001, 5012)
        # Executing according to params
        self.__scan_port_availability()

    def __scan_port_availability(self, target="localhost"):
        try:
            # scan ports
            for port in self.range:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(0.1)

                # returns an error indicator
                result = s.connect_ex((target, port))
                if result == 0:
                    self.running_servers.append((target, port))
                else:
                    self.availabilities.append((target, port))
                s.close()

        except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")
        except socket.error:
            print("\n Server not responding !!!!")
