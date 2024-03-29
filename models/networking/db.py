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

    def __init__(self, game_name: str, online: bool = False):
        self.__online = online
        if online:
            return
        self.__dir: Final = f"./Saves/{game_name}"
        self.__init_dirs()
        self.__data = []
        self.__fp = None
        self.__logger = logging.getLogger(__class__.__name__)
        self.__name: Final = "results"
        self.__file = self.__new_save()
        with open(self.__file, 'w') as fp:  # with handle errors on its own.
            json.dump(self.__data, fp)
        try:
            self.__fp = self.__renew_fp()
            self.__data = json.load(self.__fp)
        except JSONDecodeError:
            self.__data = []

    def save(self, datas: dict):
        """
        append datas to self then save to DB
        :param datas: datas to save
        :return: None
        """
        if self.__online:
            return
        self.__data.append(datas)
        self.__save()

    def __save(self):
        self.__logger.debug("saving %s", self.__data)  # data to set for print
        self.__renew_fp()
        try:
            json.dump(self.__data, self.__fp)
        except IOError:
            self.__logger.critical("Could not save to DB")
        finally:
            self.__fp.close()

    def __renew_fp(self) -> IO:
        if self.__fp:
            self.__fp.close()
        # keep fp alive, so it acts like a "Lock"
        self.__fp = open(self.__file, 'w+', encoding='utf-8')
        return self.__fp

    def __new_save(self):
        save = None
        for save in (f"./{self.__dir}/{self.__name}-{i}.json" for i in range(99999)):
            if not os.path.exists(save):
                break
        return save

    def __init_dirs(self):
        if not os.path.exists(self.__dir.split('/')[1]):
            os.mkdir(self.__dir.split('/')[1])
        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)
