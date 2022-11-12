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


class PresidentRules:
    # 4 cards of the same value played at once revert game's cards power
    USE_REVOLUTION = True
    NEW_GAME_RESET_REVOLUTION = True

    # Ta-Gueule is a rule to make player after actual one to skip his turn (like a played)
    # if the actual player plays the same set of card that is on top of the pile
    USE_TA_GUEULE = False
    # Set of rules according to rankings

    # Extreme = president-troufion
    EXTREME_RANKS = {"give": 2,   # card
                     "above": 4,  # players // Changing this value will affect medium ranks
                     "else": 1,     # cards
                     }

    # Medium = vice-vice
    MEDIUM_RANKS = {"exists_above": EXTREME_RANKS["above"],  # players
                    "give": 1,           # card
                    }

    # Rankings names and their rewards
    RANKINGS = {"President": None,  # To be defined on each game, if players leave
                "Vice-President": MEDIUM_RANKS["give"],
                "Neutre": 0,
                "Vice-Troufion": MEDIUM_RANKS["give"],
                "Troufion": None,  # To be defined on each game, if players leave
                }
