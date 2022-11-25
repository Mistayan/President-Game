import logging
from collections import Counter

import names

from models.games.card_games.card import Card
from models.players.player import Player
from rules import PresidentRules


class AI(Player):

    def __init__(self, name=None, game_pointer=None):
        """
        Instance of an AI player
        keep most of Player's logics to validate input and transaction mechanics
        :param game_pointer: CardGame (or child) Instance
        :param name: leave blank to generate random name
        """
        self.fold_counter = 0
        if not name:
            name = "AI - " + names.get_full_name(gender="female")
        super().__init__(name)
        self.__logger = logging.getLogger(self.name)
        self._is_human = False
        self.first = False
        self.game = game_pointer
        self.counter = Counter()
        self.__buffer = []
        self.got_revolution_in_hand = False

    def set_rank(self, rank_pointer):
        self.__logger.info(f"I have been assigned {rank_pointer}")
        super(AI, self).set_rank(rank_pointer)

    def _play_cli(self, n_cards_to_play=0, override=None, action='play') -> list[Card]:
        """The actual calculation method don't take into account the fact that you can break pairs
        :param n_cards_to_play: if 0, choose on its own, otherwise plays this number of cards
        :param override: Override should not be used, since the AI make decisions on its own
        :param action: action to play (play, give, ...)
        :return: Cards to play
        (they should always be valid, taking into considerations the game_pointer pile)
        """

        self.counter = Counter([card.number for card in self.hand])  # actualize counter
        self.got_revolution_in_hand = self.all_of_combo(4).total() > 0
        play = None
        if n_cards_to_play == 0:  # No previous player, choose n_cards
            self.first = True
            n_cards_to_play = self.ask_n_cards_to_play()
        if action == "play" and n_cards_to_play <= self.max_combo:
            self.__logger.debug(f"Estimating my hand : {self.hand}\tAgainst : {self.game.pile}")
            play = self.calc_best_card(n_cards_to_play)
        if action == "give" or not play:
            play = self.calc_best_card(n_cards_to_play, split=True)
        return super()._play_cli(n_cards_to_play, play or 'F')

    def play_tk(self, n_cards_to_play=0) -> list[Card]:
        """ Graphical or CLI does not matter for AI ... Only datas"""
        return self._play_cli()

    def ask_n_cards_to_play(self) -> int:
        """ pick how many cards would be wisest to be played"""
        n_cards_to_play = 1  # Default value
        if self.max_combo == 4 and \
                (self.calc_revolution_interest() <= 0.25 or
                 len(self.hand) <= 6 and self.calc_revolution_interest() < 0.5):
            n_cards_to_play = 4
        elif self.max_combo < 4:
            n_cards_to_play = self.calc_n_cards(self.max_combo,
                                                True if not self.got_revolution_in_hand else False)
        return n_cards_to_play

    def calc_revolution_interest(self) -> float:
        """ Closer To 0 means you got mainly low-power cards.
        Revolution might be considered, since values are reversed"""
        if not PresidentRules.USE_REVOLUTION:
            return 0
        self.got_revolution_in_hand = True
        counter = Counter([card.number for card in self.hand])
        total = 0
        for number, count in self.counter.items():
            total += count / (self.game.VALUES.index(number) + 1)
        mean = total / counter.total()
        self.__logger.debug(f"interest over playing revolution : {mean}")
        return mean

    def calc_n_cards(self, combo, requires_low_result=True, split=False) -> int:
        """ Calculate the actual combo interest
         compared to median combo values  / actual_combo_pairs / total_cards
         """
        total_power = 0
        total_possible_cards = 0
        total_combo_pairs = 0
        for number, count in self.counter.items():
            if count == combo or combo > 1 and (split and count == combo - 1):
                total_power += self.game.VALUES.index(number)
                total_possible_cards += self.counter[number]
                total_combo_pairs += 1
        if total_possible_cards:
            result = total_power / (self.game.revolution + 1)
            result /= (total_combo_pairs + 1)
            result *= total_possible_cards
            result /= self.counter.total()
        else:
            result = 0.042

        if not requires_low_result and result:
            result = 1 / result ** combo
        self.__logger.debug(f" My estimation for a combo of {combo} : {result:.3f}")
        if result >= 1.43 and requires_low_result and combo > 1:
            # and not (len(self.hand) < self.max_combo):
            return self.calc_n_cards(combo - 1)
            # result not satisfying, try lower combo if possible.
        self.__logger.info(f"i'm going to play {combo} cards")
        return combo

    def calc_best_card(self, nb_cards, split=False, action='play', rec_level=1):
        if self.game.check_if_played_last(self):
            self.__logger.info(f"played last, not raising myself")
            return 'F'
        _local_counter = self.counter.items()
        if self.got_revolution_in_hand:
            _local_counter = _local_counter.__reversed__()
        card = None
        for card, qty in _local_counter:
            # the card can be played no matter of the pile if first to play
            # OR if value OK according to game_pointer's pile and rules
            if self.game.card_can_be_played(card):
                if qty == nb_cards:
                    self.__logger.debug(f"my interest goes to {card} (no splits)")
                    break
                # otherwise, play a card from a split combo.
                if split or action == 'give' and {qty - 1, qty - 2} == nb_cards:
                    self.__logger.debug(f"my interest goes to {card} *** splits ***")
                    break
            card = None
        card and self.__logger.info(f"Trying: {card.__repr__()}")
        return card or \
            rec_level and self.calc_best_card(nb_cards, split=not split, rec_level=rec_level-1)
