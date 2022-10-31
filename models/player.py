from __future__ import annotations

import logging
from collections import Counter
from typing import Final

import names

from models import Card
from models.utils import human_choose_n_cards_to_play, human_choose_cards_to_play, \
    validate_human_input, player_give_card_to


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
        self._logger: Final = logging.getLogger(__class__.__name__)
        self.name: Final = name or names.get_first_name()
        self._is_human = True
        self.hand = []
        self._folded = False
        self._played_turn = False
        self._won = False
        self.last_played : list[Card] = []

    @property
    def won(self):
        return self._won

    def set_win(self, value=True):
        self._won = value

    def add_to_hand(self, card: Card) -> None:
        """ add the given Card to player's hand"""
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.hand.append(card)
        self.sort_hand()  # Replicating real life's behaviour

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
        """
        A player is considered active if he hasn't :
        folded,
        played his turn,
        won the game
        """
        active = not (self.is_folded or self.played_this_turn or self.won)
        self._logger.debug(f"{self} says i'm active") if active else None
        return active

    @property
    def is_folded(self):
        return self._folded

    def set_fold(self, status=True):
        self._logger.debug(f"{self} fold") if status else None
        self._folded = status

    @property
    def played_this_turn(self):
        return self._played_turn

    def set_played(self, value=True):
        self._logger.debug(f"{self} played") if value else None
        self._played_turn = value

    @property
    def is_human(self):
        return self._is_human

    def play_cli(self, n_cards_to_play=0) -> list[Card]:
        """Interface for a player to play with Command-line prompts (or inputs)"""
        print(f"Your hand :\n{self.hand}")
        if not n_cards_to_play:
            n_cards_to_play = human_choose_n_cards_to_play(self.max_combo)
        player_game = human_choose_cards_to_play(self, n_cards_to_play)

        return [_ for _ in player_game if _]  # Simple filtering as fail-safe

    def play_tk(self, n_cards_to_play=0) -> list[Card]:

        ...  # Pass, C style :D

    @property
    def max_combo(self):
        """
        :return: the maximum amount of cards a player can play at once
        """
        if self.hand:
            k, v = Counter([card.number for card in self.hand]).most_common(1)[0]
        else:
            v = 0
        return v

    def ask(self):
        """ Return True for Yes, False for No.
         False by default"""
        answer = False
        if self.is_human:
            _in = input(f"{self} : [Y]es / [N]o ?>").lower()
            if _in and _in[0] == "y":
                answer = True

        return answer

    def play_cards(self, n_cards_to_play: int, wanted_card: str):
        """
        Ensure there are enough of designated card in player's hand.
        Remove 1 card at a time from hand and place it in result (temporary)
        If a card is not found in player's hand, restore cards to player.

        :param n_cards_to_play: number of cards
        :param wanted_card: card to play
        :return: [card, ...] if there is enough of designated card in hand
                 [] Otherwise
        """
        result = []
        if self.is_active:
            # Validate that player has n times this card in hand
            for i in range(n_cards_to_play):
                card = validate_human_input(self, wanted_card)  # transforms wanted_card to Card
                player_give_card_to(self, card, result) if card else None
            if len(result) != n_cards_to_play:  # Not enough of designated card in hand...
                [self.add_to_hand(card) for card in result]  # Give player his cards back
                result = []

        self.last_played = result
        return result

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()

    def sort_hand(self) -> None:
        self.hand.sort()
