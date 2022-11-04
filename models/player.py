import logging
from abc import abstractmethod, ABC
from collections import Counter
from typing import Final

import names

from models.card import Card


class Player(ABC):
    """
    WARNING !!!
    Any value you put below this line,  outside __init__
    might be shared amongst different instances !!!
    """

    _is_human: bool

    @abstractmethod
    def __init__(self, name=None, game=None):
        """
        Instantiate a Player.
         Player has a name, a hand holding cards,
         can fold (stop playing for current round) receive a card or remove a card from his hand
        """
        self._logger: Final = logging.getLogger(__class__.__name__)
        self.game = game
        self.__buffer = []
        self.name: Final = name or names.get_first_name()
        self._won = False
        self._played_turn = False
        self._folded = False
        self.rank = None
        self.hand = []
        self.last_played: list[Card] = []
        self._logger.info(f"{self} joined the game")

    def reset(self):
        """ Reset most values for next game"""
        self._won = False
        self._played_turn = False
        self._folded = False
        self.hand = []
        self.__buffer = []
        self.last_played = []

    @property
    def won(self):
        return self._won

    def set_win(self, value=True):
        self._logger.info("I have won" if not len(self.hand) else "I have Lost")
        self._won = value

    @abstractmethod
    def set_rank(self, rank_pointer):
        """ set ranks to given pointer
        Method is abstract for you to implement loggers for current player"""
        self.rank = rank_pointer

    def add_to_hand(self, card: Card) -> None:
        """ add the given Card to player's hand"""
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        self._logger.debug(f"{self} received {card}\n{self.hand}")
        self.hand.append(card)
        self.sort_hand()  # Replicating real life's behaviour

    def remove_from_hand(self, card: Card) -> Card | None:
        """
        remove a specified card form player's hand.

        :param card: the card to remove from player's hand
        :return: the card removed from player's hand
        """
        if not isinstance(card, Card):
            raise ValueError("card must be an instance of Card.")
        if card in self.hand:
            self.hand.remove(card)
            self._logger.debug(f"{self} removed {card} from hand")
        else:
            card = None

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
        self._logger.debug(f"{self} says i'm {'' if active else 'not '}active")
        if not active:
            self._logger.debug("Reasons:")
            self._logger.debug("folded") if self._folded else None
            self._logger.debug("played") if self._played_turn else None
            self._logger.debug("won") if self._won else None
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

    @abstractmethod
    def play_cli(self, n_cards_to_play=0, override: str = None, action='play') -> list[Card]:
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
            n_cards_to_play = self.ask_n_cards_to_play()
        print(f"you must {action} {'a' if n_cards_to_play == 1 else ''} "
              f"{'card' if n_cards_to_play == 1 else 'cards'}")
        player_game = self.choose_cards_to_play(n_cards_to_play, override)[::]
        if player_game and len(player_game) == n_cards_to_play:
            self.__buffer = []
        else:
            [self.add_to_hand(card) for card in self.__buffer]
        return [_ for _ in player_game if _]  # Simple filtering as fail-safe

    @abstractmethod
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

    @abstractmethod
    def ask_fold(self):
        """ Implement if player should fold or not"""
        ...

    def _play_cards(self, n_cards_to_play: int, wanted_card: str):
        """
        Ensure there are enough of designated card in player's hand.
        Remove 1 card at a time from hand and place it in result (temporary)
        If a card is not found in player's hand, restore cards to player.

        :param n_cards_to_play: number of cards
        :param wanted_card: card to play
        :return: [card, ...] if there is enough of designated card in hand
                 [] Otherwise
        """
        if self.is_active:
            # Validate that player has n times this card in hand
            for i in range(n_cards_to_play):
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
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()

    def sort_hand(self) -> None:
        self.hand.sort()

    @abstractmethod
    def ask_n_cards_to_play(self) -> int:
        """ Implement logic to ask_fold the number of cards to play to player"""
        ...

    def choose_cards_to_play(self, n_cards_to_play, override: str = None):
        """ use override to force input from external sources, instead of builtins inputs
        If max_combo <= n_cards_to_play , cannot play ! (ask_fold to fold by pressing enter)
        Otherwise, player choose a card number from his hand and give N times this card.

        """
        cards_to_play = []
        if n_cards_to_play <= self.max_combo:
            _in = input(f"{n_cards_to_play} combo required: (your max : {self.max_combo})\n"
                        f"[2-9 JQKA] or 'F' to fold (you will not be able to play current round)\n") \
                .upper() if not override else override.upper()
            # Check fold status
            if not (_in and _in[0] == 'F'):
                cards_to_play = self._play_cards(n_cards_to_play, _in)
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
        if _in and not isinstance(_in, str):
            return self.validate_input(str(_in))

        _card = None
        if _in == "FOLD" or (_in and _in[0] == 'F'):
            self.set_fold()
            _card = None
        for card in self.hand:
            if card.number == _in:
                _card = card
                break
        return _card

    def choose_card_to_give(self) -> Card:
        """ PresidentGame ONLY
        According to President logic,
         """
        card = None
        if self.rank:
            if self.rank.advantage < 0:  # Give best card
                card = self.hand[-1]
            if self.rank.advantage > 0:  # Choose card to give
                card = self.play_cli(1)
        return card


class Human(Player):

    def __init__(self, name=None, game=None):
        super(Human, self).__init__(name, game)
        self._is_human = True
        self.__logger = logging.getLogger(self.name)

    def ask_n_cards_to_play(self) -> int:
        """ HUMAN ONLY
                :return: self's pick between 1 and his maximum combo
                """
        _max = self.max_combo
        n = _max if _max <= 1 else 0
        while not n > 0 or n > _max:
            try:
                n = int(input("[FIRST-PLAYER]"
                              f" - How many cards do you want to play (1-{_max})?\n?> "))
                if 0 > n > _max:
                    n = 0
            except:
                n = 0
        return 1 if n < 1 else n

    def ask_fold(self):
        """ Return True for Yes, False for No.
                 False by default"""
        answer = False
        _in = input(f"{self} : [Y]es / [N]o ?>").lower()
        if _in and _in[0] == "y":
            answer = True

        return answer

    def play_cli(self, n_cards_to_play=0, override=None, action='play') -> list[Card]:
        if not override:
            if [player.is_human for player in self.game.players].count(True) != 1:
                print(f"{self} : press Enter to start your turn\n"
                      f"(this is to avoid last player to see your hand)")
                input()

            print(f"Your hand :\n{self.hand}", flush=True)
        return super(Human, self).play_cli(n_cards_to_play, override, action=action)

    def play_tk(self, n_cards_to_play=0) -> list[Card]:
        pass

    def set_rank(self, rank_pointer):
        self.__logger.debug(f"I have been assigned {rank_pointer}")
        super(Human, self).set_rank(rank_pointer)

