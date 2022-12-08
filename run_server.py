# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""
import logging
from multiprocessing import Pool

import coloredlogs

from models import PresidentGame


def run_background(pool, game):
    return pool.apply_async(game().run_server())


if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    try:
        with Pool(processes=1, ) as pool:
            run_background(pool, PresidentGame)
    except KeyboardInterrupt as e:
        print("Server Shutting down...")
