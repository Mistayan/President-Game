from models import Card
import names


class Player:
    name: str
    cards: list[Card]

    def __init__(self, name=None):
        self.name = name or names.get_first_name()
        self.cards = []

    def add_to_hand(self, card: Card):
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.cards.append(card)

    def remove_from_hand(self, card: Card|list[Card]):
        if isinstance(card, list):
            [self.remove_from_hand(card) for card in self.cards]
            return  # End of recursive style
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.cards.remove(card)

