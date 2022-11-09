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

    # When the best card is played by someone, ends current round and starts next one
    PLAYING_BEST_CARD_END_ROUND = True

    # If set to False, you can play on the next turn.
    WAIT_NEXT_ROUND_IF_FOLD = True  # 'folded' acts like a 'played' status if False

    # Allow loser to play one last card after he ends up alone at the table
    ALLOW_FINAL_LOSER_PLAY = False

    # Set of rules according to rankings

    # Extreme = president-troufion
    EXTREME_RANKS = {"give": 1,   # card
                     "below": 4,  # players
                     "or": 2,     # cards
                     "above": 5,   # players
                     }

    # Medium = vice-vice
    MEDIUM_RANKS = {"exists_above": 5,  # players
                    "give": 1,           # card
                    }
