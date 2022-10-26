from typing import Final

from models import Card
import names


class Player:
    name: str
    hand: list[Card]
    folded: bool
    __is_human: bool

    def __init__(self, name=None):
        self.name = name or names.get_first_name()
        self.__is_human = Truechanged
        self.hand = []
        self.folded = False

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

    def is_folded(self):
        return self.folded

    def has_folded(self):
        self.folded = True

    @property
    def is_human(self):
        return self.__is_human

    def play(self, user_in, n_cards_to_play=1) -> int:
        """"""
        while True:  # While input has not been validated

            user_in = input("enter cards to play (separate with ',' for multiple values)")
            if n_cards_to_play == 1 and not user_in.count(','):
                print(f"{self._play_matching(user_in)} removed")
            elif n_cards_to_play > 1 and n_cards_to_play == user_in.count(','):
                for card in user_in.split(','):
                    print(f"{self._play_matching(card)} removed")
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
