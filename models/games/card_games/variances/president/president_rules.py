# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/26/22
"""

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

    def __repr__(self):
        return {
            "use_revolution": self.USE_REVOLUTION,
            "new_game_reset": self.NEW_GAME_RESET_REVOLUTION,
            "use_ta_gueule": self.USE_TA_GUEULE,
            "extreme": self.EXTREME_RANKS,
            "medium": self.MEDIUM_RANKS,
            "ranks": self.RANKINGS,
        }
