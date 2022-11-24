# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""
from multiprocessing import Pool

from models import PresidentGame

if __name__ == '__main__':
    with Pool(processes=1, ) as pool:
        pool.apply_async(PresidentGame().run_server(5001))
