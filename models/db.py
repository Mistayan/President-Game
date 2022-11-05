# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/02/22
"""

import json
import logging
import os.path
from json import JSONDecodeError
from typing import Final


class Database:
    """ Emulate MongoDB as a simple json file
    MongoDB requires at least Docker to run, or a fully installed version, or a server.
    To keep some simplicity in this program, it is going to be saved as a JSON
    """
    def __init__(self, game_name: str):
        self.__data = []
        self.__fp = None
        self.__logger = logging.getLogger(__class__.__name__)
        self.__file: Final = f"./saves-{game_name}.json"
        if not os.path.exists(self.__file):
            self.__logger.debug("DB does not exist, creating...")
            with open(self.__file, 'w') as fp:
                json.dump(self.__data, fp)
        try:
            self.__renew_fp()
            self.__data = json.load(self.__fp)
        except JSONDecodeError:
            self.__data = []
        self.__renew_fp()

    def update(self, datas: dict):
        self.__logger.info(f"adding {datas} to DB")
        self.__data.append(datas)
        self.__save()

    def __save(self):
        self.__logger.info(f"saving {self.__data}")
        self.__renew_fp()
        json.dump(self.__data, self.__fp)
        self.__fp.close()

    def __renew_fp(self):
        if self.__fp:
            self.__fp.close()
        # keep fp alive, so it acts like a "Lock"
        self.__fp = open(self.__file, 'w+', encoding='utf-8')
