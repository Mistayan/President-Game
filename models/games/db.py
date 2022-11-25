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
from typing import Final, IO


class Database:
    """ Emulate MongoDB as a simple json file
    MongoDB requires at least Docker to run, a fully installed version, or a server.
    To keep some simplicity in this program, it is going to be saved in memory, until game ends.
    Then, will be print to a file, once the game is over (even after keyboard interrupts).
    """

    def __init__(self, game_name: str):
        self.__dir: Final = f"./Saves/{game_name}"
        self.__init_dirs()
        self.__data = []
        self.__fp = None
        self.__logger = logging.getLogger(__class__.__name__)
        self.__name: Final = f"results"
        self.__file = self.__new_save()
        with open(self.__file, 'w') as fp:
            json.dump(self.__data, fp)
        try:
            self.__fp = self.__renew_fp()
            self.__data = json.load(self.__fp)
        except JSONDecodeError:
            self.__data = []

    def update(self, datas: dict):
        self.__logger.info(f"adding {datas} to DB")
        self.__data.append(datas)
        self.__save()

    def __save(self):
        self.__logger.debug(f"saving {self.__data}")
        self.__renew_fp()
        json.dump(self.__data, self.__fp)
        self.__fp.close()

    def __renew_fp(self) -> IO:
        if self.__fp:
            self.__fp.close()
        # keep fp alive, so it acts like a "Lock"
        self.__fp = open(self.__file, 'w+', encoding='utf-8')
        return self.__fp

    def __new_save(self):
        save = f"./{self.__dir}/{self.__name}.json"
        if os.path.exists(save):
            for save in (f"./{self.__dir}/{self.__name}-{i}.json" for i in range(99999)):
                if not os.path.exists(save):
                    break
        return save

    def __init_dirs(self):
        if not os.path.exists(self.__dir.split('/')[1]):
            os.mkdir(self.__dir.split('/')[1])
        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)
