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

from models.games.card_games import PresidentGame

if __name__ == '__main__':
    coloredlogs.set_level(logging.DEBUG)
    with Pool(processes=1, ) as pool:
        pool.apply_async(PresidentGame().run_server(5001))
