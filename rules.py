# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/05/22
"""
from abc import abstractmethod
from typing import Final, Any


# EDIT VALUES IN EACH CATEGORY AS YOU SEE FIT

class GameRules:
    # a basic card game can hold from 1 to 20 players

    @abstractmethod
    def __init__(self, total_players: int):
        self.tick_speed = 0.1  # expressed in seconds lower values means more loops runs in a second.
        self.max_players = 20
        self.min_players = 2

        if total_players < self.min_players:
            raise ValueError("Not enough players")
        if total_players > self.max_players:
            raise ValueError("Too many players")
        pass

    @abstractmethod
    def update(self, other):
        if isinstance(other, dict):
            if "max_players" in other:
                self.max_players = other.get("max_players", self.max_players)
            if "min_players" in other:
                self.min_players = other.get("min_players", self.min_players)
            if "tick_speed" in other:
                self.tick_speed = other.get("tick_speed", self.tick_speed)
        else:
            self.max_players = other.max_players
            self.min_players = other.min_players
            self.tick_speed = other.tick_speed

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        return {
            "tick_speed": self.tick_speed,
            "min_players": self.min_players,
            "max_players": self.max_players,
        }

    @abstractmethod
    def __dict__(self):
        return self.to_json()


class CardGameRules(GameRules):
    VALUES: Final = [str(num) for num in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    # color: unicode_safe
    COLORS: Final = {'♥': 'Heart', '♦': 'Square', '♠': 'Spade', '♣': 'Clover'}


    def __init__(self, total_players):
        super().__init__(total_players=total_players)
        # Player starting the first game is Queen of Heart's owner
        self.QUEEN_OF_HEART_STARTS = True

        # Player finishing the game with the best cards instantly loose instead of winning.
        self.FINISH_WITH_BEST_CARD_LOOSE = True

        # When the best card is played by someone, ends current round and starts next one
        self.PLAYING_BEST_CARD_END_ROUND = True

        # If set to False, you can play on the next turn.
        self.WAIT_NEXT_ROUND_IF_FOLD = True  # 'folded' acts like a 'played' status if False

        # If True, the loser of a game will be able to play until he finishes his hand
        self.LOSER_CAN_PLAY = False

    @abstractmethod
    def update(self, other):
        super().update(other)
        if isinstance(other, dict):
            if "queen_of_heart_start_first_game" in other:
                self.QUEEN_OF_HEART_STARTS = other.get("queen_of_heart_start_first_game")
            if "fold_means_played" in other:
                self.WAIT_NEXT_ROUND_IF_FOLD = other.get("fold_means_played")
            if "last_player_can_play_until_over" in other:
                self.LOSER_CAN_PLAY = other.get("last_player_can_play_until_over")
            if "finish_with_best_card_loose" in other:
                self.FINISH_WITH_BEST_CARD_LOOSE = other.get("finish_with_best_card_loose",
                                                             self.FINISH_WITH_BEST_CARD_LOOSE)
            if "playing_best_card_end_round" in other:
                self.PLAYING_BEST_CARD_END_ROUND = other.get("playing_best_card_end_round",
                                                             self.PLAYING_BEST_CARD_END_ROUND)
        else:
            self.QUEEN_OF_HEART_STARTS = other.QUEEN_OF_HEART_STARTS
            self.FINISH_WITH_BEST_CARD_LOOSE = other.FINISH_WITH_BEST_CARD_LOOSE
            self.PLAYING_BEST_CARD_END_ROUND = other.PLAYING_BEST_CARD_END_ROUND
            self.WAIT_NEXT_ROUND_IF_FOLD = other.WAIT_NEXT_ROUND_IF_FOLD
            self.LOSER_CAN_PLAY = other.LOSER_CAN_PLAY

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.update({
            "values": self.VALUES,
            "colors": [safe for unsafe, safe in self.COLORS.items()],
            "queen_of_heart_start_first_game": self.QUEEN_OF_HEART_STARTS,
            "finish_with_best_card_loose": self.FINISH_WITH_BEST_CARD_LOOSE,
            "playing_best_card_end_round": self.PLAYING_BEST_CARD_END_ROUND,
            "last_player_can_play_until_over": self.LOSER_CAN_PLAY,
            "fold_means_played": self.WAIT_NEXT_ROUND_IF_FOLD,
        })
        return ret

    def __dict__(self) -> dict[str, Any]:
        return self.to_json()


class PresidentRules(CardGameRules):
    min_players = 3
    max_players = 6


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
        super().__init__(total_players=nb_players)
        self.nbp = nb_players
        # revolution : 4 cards of the same value played at once revert game's cards powers
        self.use_revolution = True
        self.new_game_reset_revolution = True

        # Ta-Gueule is a rule to make player after actual one to skip his turn (like a played)
        # if the actual player plays the same set of card that is on top of the pile
        self.use_ta_gueule = False

    def update(self, other):
        super().update(other)
        if isinstance(other, dict):
            if "use_revolution" in other:
                self.use_revolution = other.get("use_revolution", self.use_revolution)
            if "new_game_reset_revolution" in other:
                self.new_game_reset_revolution = other.get("new_game_reset_revolution", self.new_game_reset_revolution)
            if "use_ta_gueule" in other:
                self.use_ta_gueule = other.get("use_ta_gueule", self.use_ta_gueule)
            if "extreme_ranks" in other:
                self.EXTREME_RANKS = other.get("extreme_ranks", self.EXTREME_RANKS)
            if "medium_ranks" in other:
                self.MEDIUM_RANKS = other.get("medium_ranks", self.MEDIUM_RANKS)
            if "rankings" in other:
                self.RANKINGS = other.get("rankings", self.RANKINGS)
        else:
            self.use_revolution = other.use_revolution
            self.new_game_reset_revolution = other.new_game_reset_revolution
            self.use_ta_gueule = other.use_ta_gueule
            self.EXTREME_RANKS = other.EXTREME_RANKS
            self.MEDIUM_RANKS = other.MEDIUM_RANKS
            self.RANKINGS = other.RANKINGS

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.update({
            "use_revolution": self.use_revolution,
            "new_game_reset_revolution": self.new_game_reset_revolution,
            "use_ta_gueule": self.use_ta_gueule,
            "extreme_ranks": self.EXTREME_RANKS,
            "medium_ranks": self.MEDIUM_RANKS,
            "rankings": self.RANKINGS,
        })
        return ret

    def __dict__(self) -> dict[str, Any]:
        return self.to_json()
