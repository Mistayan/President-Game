# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/05/22
"""

from typing import Final, Any


# EDIT VALUES IN EACH CATEGORY AS YOU SEE FIT

class GameRules:
    # a basic card game can hold from 1 to 20 players
    TICK_SPEED = 0.1  # expressed in seconds lower values means more loops runs in a second.
    MAX_PLAYERS = 20
    MIN_PLAYERS = 1

    VALUES: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    # color: unicode_safe
    COLORS: Final = {'♥': 'Heart', '♦': 'Square', '♠': 'Spade', '♣': 'Clover'}

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

    def __repr__(self) -> dict[str, Any]:
        return {
            "cards_values": self.VALUES,
            "cards_colors": [safe for unsafe, safe in self.COLORS.items()],
            "queen_of_heart_start_first_game": self.QUEEN_OF_HEART_STARTS,
            "finish_with_best_card_lose": self.FINISH_WITH_BEST_CARD__LOOSE,
            "playing_best_card_end_round": self.PLAYING_BEST_CARD_END_ROUND,
            "last_player_can_play_until_over": self.LOSER_CAN_PLAY,
            "fold_means_played": self.WAIT_NEXT_ROUND_IF_FOLD,
        }

    def __dict__(self):
        return self.__repr__()


class PresidentRules:
    MIN_PLAYERS = 3
    MAX_PLAYERS = 6

    # revolution : 4 cards of the same value played at once revert game's cards powers
    USE_REVOLUTION = True
    NEW_GAME_RESET_REVOLUTION = True

    # Ta-Gueule is a rule to make player after actual one to skip his turn (like a played)
    # if the actual player plays the same set of card that is on top of the pile
    USE_TA_GUEULE = False

    # Set of rules according to rankings

    # Extreme = president-troufion
    EXTREME_RANKS = {"give": 2,  # card
                     "above": 4,  # players // Changing this value will affect medium ranks
                     "else": 1,  # cards
                     }

    # Medium = vice-vice
    MEDIUM_RANKS = {"exists_above": EXTREME_RANKS["above"],  # players
                    "give": 1,  # card
                    }

    # Rankings names and their rewards
    RANKINGS = {"President": None,  # To be defined on each game, if players leave
                "Vice-President": MEDIUM_RANKS["give"],
                "Neutre": 0,
                "Vice-Troufion": MEDIUM_RANKS["give"],
                "Troufion": None,  # To be defined on each game, if players leave
                }

    def __init__(self, nb_players):
        self.nbp = nb_players

    def __repr__(self) -> dict[str, Any]:
        return {
            "use_revolution": self.USE_REVOLUTION,
            "new_game_reset": self.NEW_GAME_RESET_REVOLUTION,
            "use_ta_gueule": self.USE_TA_GUEULE,
            "extreme": self.EXTREME_RANKS,
            "medium": self.MEDIUM_RANKS,
            "ranks": self.RANKINGS,
        }

    def __dict__(self):
        return self.__repr__()
