from __future__ import annotations
from typing import Final
from collections import Counter
import names

from models import Card
from models.utils import human_choose_n_cards_to_play, human_choose_cards_to_play


class Player:
    name: str
    hand: list
    _folded: bool = False
    _is_human: bool
    _played_turn: bool = False
    _won: bool = False

    def __init__(self, name=None):
        """
        Instantiate a Player.
         Player has a name, a hand holding cards,
         can fold (stop playing for current round) receive a card or remove a card from his hand
        """
        self.name: Final = name or names.get_first_name()
        self._is_human = True
        self.hand = []
        self._folded = False
        self._played_turn = False
        self._won = False
        self._lost = False

    @property
    def won(self):
        return self._won

    def add_to_hand(self, card: Card) -> None:
        """ add the given Card to player's hand"""
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.hand.append(card)
        self.hand.sort()

    def remove_from_hand(self, card: Card) -> Card:
        """
        remove a specified card form player's hand.

        :param card: the card to remove from player's hand
        :return: the card removed from player's hand
        """
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.hand.remove(card)
        return card

    @property
    def is_active(self):
        return not self.is_folded and not self.played_this_turn \
               and not self.won and not self._lost

    @property
    def is_folded(self):
        return self._folded

    def set_fold(self, status=True):
        self._folded = status

    @property
    def played_this_turn(self):
        return self._played_turn

    def set_played(self, value=True):
        self._played_turn = value

    def set_win(self):
        self._won = True

    def set_lost(self):
        self._lost = True

    @property
    def is_human(self):
        return self._is_human

    @property
    def max_playable_card(self):
        """ Returns the most common card's count"""
        count = Counter(card.number for card in self.hand).most_common(1)[0]
        k, v = count
        return v

    def play_cli(self, n_cards_to_play=0, rev=False) -> list[Card]:
        """"""
        print(f"Your hand :\n{self.hand if not rev else self.hand[::-1]}")
        if not n_cards_to_play:
            n_cards_to_play = human_choose_n_cards_to_play(self.max_playable_card)
        player_game = human_choose_cards_to_play(self, n_cards_to_play)

        return [_ for _ in player_game if _]  # Simple filtering

    def play_tk(self, n_cards_to_play=0) -> list[Card]:

        ...  # Pass, C style :D

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()

    def sort_hand(self) -> None:
        self.hand.sort()
