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
