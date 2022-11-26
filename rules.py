# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/05/22
"""

from typing import Final


# EDIT VALUES IN EACH CATEGORY AS YOU SEE FIT

class GameRules:
    # a basic card game can hold from 1 to 20 players
    TICK_SPEED = 0.1  # expressed in seconds lower values means more loops runs in a second.
    MAX_PLAYERS = 20
    MIN_PLAYERS = 1

    VALUES: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    # color: unicode_safe
    COLORS: Final = {'♡': 'Heart', '♦': 'Square', '♤': 'Spade', '♣': 'Clover'}

    # Player starting the first game is Queen of Heart's owner
    QUEEN_OF_HEART_STARTS = True

    # Player finishing the game with the best cards instantly loose instead of winning.
    FINISH_WITH_BEST_CARD__LOOSE = False

    # When the best card is played by someone, ends current round and starts next one
    PLAYING_BEST_CARD_END_ROUND = True

    # If set to False, you can play on the next turn.
    WAIT_NEXT_ROUND_IF_FOLD = True  # 'folded' acts like a 'played' status if False

    # If True, the loser of a game will be able to play until he finishes his hand
    LOSER_CAN_PLAY = False

    def __init__(self):
        pass

    def __repr__(self):
        return {
            "cards_values": self.VALUES,
            "cards_colors": [safe for unsafe, safe in self.COLORS.items()],
            "queen_of_heart_start_first_game": self.QUEEN_OF_HEART_STARTS,
            "finish_with_best_ard__lose": self.FINISH_WITH_BEST_CARD__LOOSE,
            "playing_best_card_end_round": self.PLAYING_BEST_CARD_END_ROUND,
            "last_player_can_play_until_over": self.LOSER_CAN_PLAY,
            "fold_means_played": self.WAIT_NEXT_ROUND_IF_FOLD,
        }
