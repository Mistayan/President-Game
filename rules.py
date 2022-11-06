# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/05/22
"""


class GameRules:
    # EDIT VALUES BELLOW AS YOU SEE FIT

    # 4 cards of the same value played at once revert game's cards power
    USE_REVOLUTION = False

    # Player starting the first game is Queen of Heart's owner
    QUEEN_OF_HEART_STARTS = True

    # Player finishing the game with the best cards instantly loose instead of winning.
    FINISH_WITH_BEST_CARD__LOOSE = False

    # When the best card is played by someone, end current round
    PLAYING_BEST_CARD_END_ROUND = False

    # If set to False, you can play on the next turn.
    WAIT_NEXT_ROUND_IF_FOLD = False
