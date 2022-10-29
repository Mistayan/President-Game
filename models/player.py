from typing import Final

import names

from models import Card


class Player:
    name: str
    hand: list
    folded: bool
    _is_human: bool

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

    def add_to_hand(self, card: Card) -> None:
        """ add the given Card to player's hand"""
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.hand.append(card)

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
    def is_folded(self):
        return self._folded

    def folds(self, status=True):
        self._folded = status

    @property
    def is_human(self):
        return self._is_human

    def play(self, card, n_cards_to_play=1) -> int:
        """"""

        return n_cards_to_play

    def _play_matching(self, string) -> Card:
        if string in self.hand:
            matching_card = None
            for card in self.hand:
                if card.number == string:
                    matching_card = card
                    self.remove_from_hand(matching_card)
                    return matching_card
        raise IndexError(f"{string} not found in {self.hand}")

    def __str__(self):
        return f"{self.name}"

    def sort_hand(self) -> None:
        self.hand.sort()

