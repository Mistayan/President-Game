from models import Card
import names


class Player:
    name: str
    hand: list[Card]
    folded: bool

    def __init__(self, name=None):
        self.name = name or names.get_first_name()
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

    def __str__(self):
        return f"{self.name}"
