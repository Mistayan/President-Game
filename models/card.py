import models


class Card:

    def __init__(self, number, color):
        """
        Instantiate a Card for a Deck
        :param number: the strength of the card
        :param color: the color of the card
        """
        self.validate(number, color)
        self.number = number
        self.color = color

    @staticmethod
    def validate(num, color):
        """ validate if num and color are valid inputs """
        if str(num) not in models.VALUES:
            raise ValueError(f"card number is not in {models.VALUES}")
        if color not in models.COLORS:
            raise ValueError("card color must be ♡ or ♤")

    def __eq__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = models.VALUES.index(self.number)
        other_i = models.VALUES.index(other.number)
        return self_i == other_i

    def __gt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = models.VALUES.index(self.number)
        other_i = models.VALUES.index(other.number)
        return self_i > other_i

    def __lt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = models.VALUES.index(self.number)
        other_i = models.VALUES.index(other.number)
        return self_i < other_i

    def __str__(self):
        return f"{self.number}{self.color}"

    def __repr__(self):
        return self.__str__()
