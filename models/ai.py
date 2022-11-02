import logging

import names

from models.player import Player, Card


def calc_revolution_interest():
    pass


class AI(Player):

    def __init__(self, name=None, game=None):
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
        self.game = game
        self.counter = Counter()
        self.__buffer = []
        self.got_revolution_in_hand = False

    def play_cli(self, n_cards_to_play=0, override=None) -> list[Card]:
        """The actual calculation method don't take into account the fact that you can break pairs.
        :param n_cards_to_play: if 0, choose on its own, otherwise plays this number of cards
        :param override: Override should not be used, since the AI make decisions on its own.
        :return: Cards to play
        (they should always be valid, taking into considerations the game pile)
        """
        self.counter = Counter([card.number for card in self.hand])  # actualize counter
        play = None
        if n_cards_to_play == 0:  # No previous player, choose n_cards
            n_cards_to_play = self.ask_n_cards_to_play()
        if n_cards_to_play <= self.max_combo:
            print("Estimating my hand... ")
            play = self.calc_best_card(n_cards_to_play)
        return super().play_cli(n_cards_to_play, play or 'F')

    def play_tk(self, n_cards_to_play=0) -> list[Card]:
        """ Graphical or CLI does not matter for AI ... Only datas"""
        return self.play_cli()

    def ask_fold(self):
        pass

    def ask_n_cards_to_play(self) -> int:
        pass

