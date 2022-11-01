import logging

import names

from models.player import Player, Card


def calc_revolution_interest():
    pass


class AI(Player):

    def __init__(self, game, name=None):
        """
        Instance of an AI player
        keep most of Player's logics to validate input and transaction mechanics


        :param game: CardGame Instance
        :param name: leave blank to generate random name
        """
        if not name:
            name = "AI - " + names.get_full_name(gender="female")
        super().__init__(name)
        self.__logger = logging.getLogger(self.name)
        self._is_human = False
        self.game_link = game

    def play_cli(self, n_cards_to_play=0, override=None) -> list[Card]:
        if n_cards_to_play == 0:
            # I start
            ...
        if self.max_combo == 4:
            calc_revolution_interest()
        return

    def play_tk(self, n_cards_to_play=0) -> list[Card]:
        return self.play_cli()

    def ask_fold(self):
        pass

    def ask_n_cards_to_play(self) -> int:
        pass

