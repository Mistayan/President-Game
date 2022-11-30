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
        interface.menu()  # Connect or exit
        try:
            while interface.update():  # As long as we are connected, with no errors
                if interface.action_required is True:
                    interface.request_player_action()
                elif interface.game_dict['running'] is False:
                    interface.menu()
        except KeyboardInterrupt as e:
            print("Shutting down Interface...")
