# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/20/22
"""
import logging

import coloredlogs

from models.interfaces import Interface
from models.players import Human

if __name__ == '__main__':
    coloredlogs.set_level(logging.INFO)
    with Interface(Human(input("Player Name ?"))) as interface:  # With, auto-disconnect on exit
        interface.run_interface()
