from models.conf import VALUES, COLORS


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
        if str(num) not in VALUES:
            raise ValueError(f"card number is not in {VALUES}")
        if color not in COLORS:
            raise ValueError("card color must be ♡ or ♤")

    def __eq__(self, other):
        """ test card's numbers equity (see __ne__ for value & color comparison) """
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_value = VALUES.index(self.number)
        other_value = VALUES.index(other.number)
        return self_value == other_value

    def __ne__(self, other):
        """ Ensure cards are different even if __eq__ is True"""
        self_color = COLORS.index(self.color)
        other_color = COLORS.index(other.color)
        return self == other and self_color == other_color

    def __gt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = VALUES.index(self.number)
        other_i = VALUES.index(other.number)
        return self_i > other_i

    def __ge__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = VALUES.index(self.number)
        other_i = VALUES.index(other.number)
        return self_i >= other_i

    def __lt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = VALUES.index(self.number)
        other_i = VALUES.index(other.number)
        return self_i < other_i

    def __str__(self):
        return f"{self.number}{self.color}"

    def __repr__(self):
        return self.__str__()
