# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 01/10/22
"""

import names

from models.games import PresidentGame

if __name__ == '__main__':
    # INIT
    game = PresidentGame(nb_players=1, nb_ai=3)
    for i in range(len(game.players)):
        if game.players[i].is_human:
            game.players[i].name = input("Player Name ?") or names.get_full_name()
    # Start the game. (no TK so far)
    game.start()
