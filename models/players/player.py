from __future__ import annotations
import logging
from models.card import Card
from .player_template import Player


class Human(Player):

    def __init__(self, name=None, game=None):
        super(Human, self).__init__(name, game)
        self._is_human = True
        self.__logger = logging.getLogger(self.name)

    def ask_n_cards_to_play(self) -> int:
        """ HUMAN ONLY
        :return: self's pick between 1 and his maximum combo
        """
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
        return super(Human, self)._play_cli(n_cards_to_play, override, action=action)

    def play_tk(self, n_cards_to_play=0) -> list[Card]:
        pass
