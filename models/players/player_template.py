# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/10/22
"""
from __future__ import annotations

import logging
import time
from abc import abstractmethod, ABC
from collections import Counter
from typing import Final

import names

from models.games.card_games.card import Card
from models.networking.plays import GamePlay
from models.utils import SerializableObject
from rules import PresidentRules, CardGameRules, GameRules


class Player(SerializableObject, ABC):
    """ The Base Player Template """
    # WARNING !!!
    # Any value you put below this line,  outside __init__
    # might be shared amongst different instances !!!
    _is_human: bool

    @abstractmethod
    def __init__(self, name=None, game=None):
        """
        Instantiate a Player.
         Player has a name, a hand holding cards,
         can fold (stop playing for current round) receive a card or remove a card from his hand
        """
        super().__init__()
        self.game_rules = None
        self.plays = []
        self._logger: Final = logging.getLogger(__class__.__name__)
        self.game = game
        self.__buffer = []
        self.name: Final = name or names.get_first_name()
        self._won = False
        self._played_turn = False
        self._folded = False
        self.is_action_required = False  # Required for Interface -> Game actions to happen
        self.rank = None
        self.hand = []
        self.last_played: list[GamePlay] = []

    def set_game_rules(self, rules: GameRules | CardGameRules | PresidentRules) -> None:
        """ Set player's internal game rules pointer (client side only ?)"""
        if not isinstance(rules, (GameRules, CardGameRules, PresidentRules)):
            raise ValueError("rules must be an instance of GameRules.")
        self.game_rules = rules

    @abstractmethod
    def _play_cli(self, n_cards_to_play=0, override: str = None, action='play') -> list[Card]:
        """Interface for a player to play with Command-line prompts (or inputs)
        use override to use external inputs (AI / Tk / ...)
        This is done to display results in CLI, even for external uses.

        How to use:
        play_cli(number_of_cards_to_play = 0) Will ask n_cards and card(s) to play
        play_cli(number_of_cards_to_play > 1) Will input to ask a card to play N times
        play_cli(number_of_cards_to_play > 1, override = Any_of(VALUES)) plays without inputs
        :param n_cards_to_play: the number of the same card to play
        :param override: . Leave empty to be prompted via CLI
        :param action: the action to be played (play, give, ...)
        """
        if not n_cards_to_play:
            self._logger.info("Choose N card to %s", action)
            n_cards_to_play = self.ask_n_cards_to_play()
        player_game = self.choose_cards_to_play(n_cards_to_play, override)
        self._logger.debug(player_game)
        if player_game and len(player_game) == n_cards_to_play:
            self.__buffer = []
        elif not self.folded:
            self._logger.debug("not enough cards in hand")
            [self.add_to_hand(card) for card in self.__buffer]
        return player_game

    @abstractmethod
    def ask_n_cards_to_play(self) -> int:
        """ Implement logic to ask the number of cards to play to player"""

    @property
    def won(self) -> bool:
        """ returns True if player won """
        return self._won

    def reset(self):
        """ Reset most values for next game"""
        self._won = False
        self._played_turn = False
        self._folded = False
        self.is_action_required = False
        self.hand = []
        self.__buffer = []
        self.last_played = []

    def set_game(self, game):
        """ Set player's internal game pointer (server side only)"""
        self.game = game

    def set_win(self, value: bool = True) -> None:
        """ set _won to given value"""
        if value:
            self._logger.info("%s %s", self, 'have won' if not self.hand else 'have Lost')
        self._won = value

    def set_rank(self, rank_pointer) -> None:
        """ set ranks to given pointer"""
        self.rank = rank_pointer

    def set_fold(self, value=True) -> None:
        """ set fold to given value (True by default)"""
        value and self._folded is False and self._logger.info("%s folds", self.name)
        self._folded = value

    def set_played(self, value=True) -> None:
        """
        set played to given value (True by default)
         if played, his action is no longer required
        """
        if value:
            self._logger.info("%s played", self.name)
        self._played_turn = value
        if self.played:
            self.is_action_required = False

    def add_to_hand(self, card: Card) -> None:
        """ add the given Card to player's hand"""
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self.hand.append(card)
        self._logger.debug("%s received %s", self, card.unicode_safe())
        self.sort_hand()  # Replicating real life's behaviour

    def remove_from_hand(self, card: Card) -> Card | None:
        """
        remove a specified card form player's hand
        :param card: the card to remove from player's hand
        :return: the card removed from player's hand
        """
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        if card in self.hand:
            self.hand.remove(card)
            self._logger.debug("%s removed %s from hand", self, card.unicode_safe())
        else:
            card = None

        return card

    @property
    def is_active(self) -> bool:
        """
        A player is considered active if he hasn't :
        folded,
        played his turn,
        won the game
        """
        active = not self.folded and not self.played and not self.won and len(self.hand)
        self._logger.debug("%s says i'm%s active", self, '' if active else ' not')
        if not active:
            reasons = f"Reasons: {'won.' if self._won else ''}" \
                      f"{'folded. ' if not self._won and self.folded else ''}" \
                      f"{'played. ' if not self._won and self.played else ''}"
            self._logger.debug(reasons)
        return active

    @property
    def folded(self) -> bool:
        """ return player fold status """
        return self._folded

    @property
    def played(self) -> bool:
        """ return player play status """
        return self._played_turn

    @property
    def is_human(self):
        """ return player human condition """

        return self._is_human

    @property
    def hand_as_numbers(self):
        """ return cards from hand as numbers only """
        return [card.number for card in self.hand]

    @property
    def hand_as_colors(self):
        """ return cards from hand as colors only """
        return [self.game.game_rules.COLORS[card.color] for card in self.hand]

    @property
    def max_combo(self):
        """ return the maximum amount of cards a player can play at once """
        if self.hand:
            _, val = Counter(self.hand_as_numbers).most_common(1)[0]
        else:
            val = 0
        return val

    def all_of_combo(self, combo) -> Counter:
        """
        :param combo: wanted N combo cards from hand
        :return: combos that match wanted count
        """
        return Counter((card, count) for card, count in Counter(self.hand_as_numbers).items()
                       if count == combo)

    def ask_yes_no(self, question: str, override: bool = False) -> bool:
        """ Return True for Yes, False for No.
                 False by default"""
        answer = override
        if not answer:
            _in = input(f"{self}, {question} (y/n) ?>").lower()
            if _in and _in[0] == "y":
                answer = True
        return answer

    def _play_cards(self, n_cards_to_play: int, wanted_card: str) -> list[Card]:
        """
        Ensure there are enough of designated card in player's hand.
        Remove 1 card at a time from hand and place it in result (temporary)
        If a card is not found in player's hand, restore cards to player
        :param n_cards_to_play: number of cards
        :param wanted_card: card to play
        :return: [card, ...] if there is enough of designated card in hand
                 [] Otherwise
        """
        if self.is_active:
            # Validate that player has n times this card in hand
            for _ in range(n_cards_to_play):
                card = self.validate_input(wanted_card)  # transforms wanted_card to Card
                if card:
                    self.__buffer.append(self.remove_from_hand(card))
            if len(self.__buffer) != n_cards_to_play:  # Not enough of designated card in hand...
                self._logger.info("Not enough cards")
                [self.add_to_hand(card) for card in self.__buffer]  # Give player his cards back
                self.__buffer = []

        self.last_played = self.__buffer
        return self.__buffer

    def __str__(self):
        """obj as string"""
        return f"{self.name}"

    def __repr__(self):
        """obj as complex repr"""
        return self.__str__()

    def sort_hand(self) -> None:
        """ Sort player's hand by cards power."""
        self.hand.sort()

    def choose_cards_to_play(self, n_cards_to_play, override: str = None) -> list[Card]:
        """ use override to force input from external sources, instead of builtins inputs
        If max_combo <= n_cards_to_play , cannot play ! (ask to fold by pressing enter)
        Otherwise, player choose a card number from his hand and give N times this card.
        """
        cards_to_play = []
        self._logger.info("Choose cards x %d", n_cards_to_play)
        self._logger.debug("must play %d; my max is %d", n_cards_to_play, self.max_combo)
        if n_cards_to_play <= self.max_combo:
            _in = input("[2-9 JQKA] or 'F' to fold"
                        f"{'(you will not be able to play current round)' if self.game_rules.wait_next_round_if_folded else ''}\n") \
                .upper() if not override else override.upper()
            # Check fold status
            if not (_in and _in[0] == 'F'):
                cards_to_play = self._play_cards(n_cards_to_play=n_cards_to_play, wanted_card=_in)
            else:
                self.set_fold()  # True by default
        elif not override:
            input("Cannot play. Press enter to fold")
            self.set_fold()  # True by default
        if override and not cards_to_play:
            self._logger.info("".join(["!" * 20, f" {self} Could Not Play ", "!" * 20]))
            self.set_fold()  # True by default
        return cards_to_play

    def validate_input(self, _in: str) -> Card | None:
        """ Ensure the data given is valid """
        if _in and not isinstance(_in, str):
            return self.validate_input(str(_in))

        _card = None
        if _in == "FOLD" or (_in and _in[0] == 'F'):
            self.set_fold()
        else:
            for card in self.hand:
                if card.number == _in:
                    _card = card
                    break
        return _card

    def choose_cards_to_give(self) -> Card:
        """ PresidentGame ONLY
        According to President logic,
         """
        self.is_action_required = True

        card = None
        if self.rank:
            adv = self.rank.advantage  # Evaluate only once
            if adv < 0:  # Give best card
                card = self.hand[-1]
            if adv > 0:  # Choose card to give
                card = self._play_cli(n_cards_to_play=1, action='give')
        return card

    def play(self, required_cards):
        """ allows player to play according to his interface preferences """
        self._logger.info("%s playing", self.name)
        if not self.game or not self.is_human:  # local side
            return self._play_cli(n_cards_to_play=required_cards)
        if self.is_human and self.game:  # server side
            return self.wait_response()

    def __eq__(self, other: Player | str) -> bool:
        ret = False
        if isinstance(other, str):
            ret = self.name == other
        elif isinstance(other, Player):
            ret = self.name == other.name
        return ret

    def wait_response(self):
        """ Await timeout or player's action (asynchronously)"""
        timeout_counter = 10
        while self.plays is None:
            time.sleep(0.3)
            timeout_counter -= 1
        if timeout_counter <= 0:
            return []
        return self.plays
