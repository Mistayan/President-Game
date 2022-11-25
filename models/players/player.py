from __future__ import annotations

import logging
import secrets

from models.games.card_games.card import Card
from rules import GameRules
from .player_template import Player


class Human(Player):

    def __init__(self, name=None, game=None):
        super(Human, self).__init__(name, game)
        self._is_human = True
        self.__logger = logging.getLogger(__class__.__name__)
        self.__token = None
        self.messages: list[dict] = []

    def renew_token(self):
        self.__token = secrets.token_hex(100)
        self.__logger.debug(f"Updated token to {self.__token}")

    @property
    def token(self):
        return self.__token

    def ask_n_cards_to_play(self) -> int:
        """ HUMAN ONLY
        :return: self's pick between 1 and his maximum combo
        """
        self.__logger.info("Choose N card")
        _max = self.max_combo
        n = _max if _max <= 1 else 0
        while not n > 0 or n > _max:
            try:
                n = int(input("[FIRST-PLAYER]"
                              f" - How many cards do you want to play (1-{_max})?\n?> "))
                if 0 > n > _max:
                    n = 0
            except ValueError:
                n = 0
        return 1 if n < 1 else n

    def _play_cli(self, n_cards_to_play=0, override=None, action='play') -> list[Card]:
        if not override:
            print(f"Your hand :\n{self.hand}", flush=True)
            n_cards_to_play and print(f"you must {action} "
                                      f" {'a card' if n_cards_to_play == 1 else n_cards_to_play} "
                                      f"{'' if n_cards_to_play == 1 else 'cards'}")
        return super(Human, self)._play_cli(n_cards_to_play, override, action=action)

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
            'action_required': self.action_required
        }

    def from_json(self, _json: dict):
        self.__update_hand(_json)
        self.__update_status(_json)

    def __update_hand(self, _json: dict):
        assert len(_json["hand_n"]) == len(_json["hand_c"])
        cards = []
        for i, color in enumerate(_json["hand_c"]):
            for unsafe, safe in GameRules.COLORS.items():
                if safe == color:
                    cards.append(Card(_json["hand_n"][i], unsafe))
        self.hand = cards

    def __update_status(self, _json: dict):
        self.action_required = _json.get("action_required")
        self.set_played(_json.get("played"))
        self.set_fold(_json.get("folded"))
        self.set_win(_json.get("finished"))
        if _json.get("messages"):
            for info in _json.get('messages'):
                if isinstance(info, dict) and info.get('message') == "Info":
                    print(info['content'])
                else:
                    print(info)
