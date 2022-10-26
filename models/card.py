from typing import Final


class Card:
    __values: Final = [str(_) for _ in range(3, 11)] + ["J", "Q", "K", "A", "2"]
    __colors: Final = {'♡', '♦', '♤', '♣'}

    def __init__(self, number, color):
        """
        Instantiate a Card for a Deck
        :param number: the strength of the card
        :param color: the color of the card
        """
        self.validate(number, color)
        self.number = number
        self.color = color

    def validate(self, num, color):
        """
        validate if num and color are valid inputs
        :return:
        """
        if str(num) not in self.__values:
            raise ValueError(f"card number is not in {self.__values}")
        if color not in self.__colors:
            raise ValueError("card color must be ♡ or ♤")

    def __eq__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = self.__values.index(self.number)
        other_i = self.__values.index(other.number)
        return self_i == other_i

    def __gt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = self.__values.index(self.number)
        other_i = self.__values.index(other.number)
        return self_i > other_i

    def __lt__(self, other):
        if not other or not self:
            raise ValueError("Cannot compare to Empty Element")
        self_i = self.__values.index(self.number)
        other_i = self.__values.index(other.number)
        return self_i < other_i

    def __str__(self):
        return f"{self.number}{self.color}"

    def __repr__(self):
        return self.__str__()
