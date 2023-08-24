# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
from __future__ import annotations

import logging
import secrets

from models.games.card_games.card import Card
from rules import CardGameRules
from .player_template import Player


class Human(Player):
    """ a Human player"""

    def __init__(self, name=None, game=None):
        """ Instantiate a Human player """
        super().__init__(name, game)
        self._is_human = True
        self.__logger = logging.getLogger(__class__.__name__)
        self.__token = None
        self.messages: list[dict] = []

    def renew_token(self):
        """ generate a new random token """
        self.__token = secrets.token_hex(100)
        self.__logger.debug("Updated token to %s", self.__token)

    @property
    def token(self):
        """ returns player's token"""
        return self.__token

    def ask_n_cards_to_play(self) -> int:
        """ HUMAN ONLY
        :return: self's pick between 1 and his maximum combo
        """
        _max = self.max_combo
        n_cards = _max if _max <= 1 else 0
        while n_cards <= 0 or n_cards > _max:
            try:
                n_cards = int(input("[FIRST-PLAYER]"
                                    f" - How many cards do you want to play (1-{_max})?\n?> "))
                if 0 > n_cards > _max:
                    n_cards = 0
            except ValueError:
                n_cards = 0
        return 1 if n_cards <= 1 else n_cards

    def _play_cli(self, n_cards_to_play=0, override=None, action='play') -> list[Card]:
        if not override:
            print(f"Your hand :\n{self.hand}", flush=True)
            if n_cards_to_play:
                print(f"you must {action} "
                      f" {'a card' if n_cards_to_play == 1 else n_cards_to_play} "
                      f"{'' if n_cards_to_play == 1 else 'cards'}")
        return super()._play_cli(n_cards_to_play, override, action=action)

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'hand_n': self.hand_as_numbers,
            'hand_c': self.hand_as_colors,
            'played': self.played,
            'folded': self.folded,
            'finished': self.won,
            'last_played': [_.unicode_safe() for _ in self.last_played],
            'messages': self.messages,
            'action_required': self.is_action_required,
            'rank': self.rank and self.rank.rank_name
        }

    def from_json(self, _json: dict):
        """ Turn json datas to actual player's datas """
        self.__update_hand(_json.get("hand_c"), _json.get("hand_n"))
        self.__update_status(_json)

    def __update_hand(self, hand_c: list[str], hand_n: list[int]):
        """ from json, update hand (sent from server) """
        assert len(hand_n) == len(hand_c)
        cards = []
        for unsafe, safe in CardGameRules.COLORS.items():
            for i, color in enumerate(hand_c):
                if safe == color:
                    cards.append(Card(hand_n[i], unsafe))
        self.hand = cards

    def __update_status(self, _json: dict):
        """ from json, update player's status (sent from server)"""
        self.is_action_required = _json.get("action_required")
        self.set_played(_json.get("played"))
        self.set_fold(_json.get("folded"))
        self.set_win(_json.get("finished"))
        if _json.get("messages"):
            for info in _json.get('messages'):
                if isinstance(info, dict) and info.get('message') == "Info":
                    print(info['content'])
                else:
                    print(info)
