import logging

import coloredlogs as coloredlogs
import names

from models import Player, AI, Deck, Card

coloredlogs.install()
logger = logging.getLogger(__name__)


class PresidentGame:
    players: list
    turn: int = 0

    def __init__(self, number_of_players=3, number_of_ai=0, *players_names):
        """
        Game Instance.
        Players (includes IA) : 3-6 players
        :param number_of_players: int 1-6
        :param number_of_ai: int 1-5
        :param players_names: "p1", "p2", ..., "p6"
        """
        if players_names and len(players_names) > number_of_players:
            raise IndexError(f"Too many names for Human Player count (AI are randomly named)")
        if 3 < number_of_players + number_of_ai > 6:
            raise ValueError(f"Invalid Total Number of Players. 3-6")

        self.players = []
        for name in players_names:  # Named players
            self.players += [Player(str(name))]
            number_of_players -= 1
        for _ in range(number_of_players):  # Anonymous Players
            self.players += [Player()]
        self.players += [AI("AI - " + names.get_full_name(gender="female"))
                         for _ in range(number_of_ai)]  # AI Players
        self.deck = Deck().shuffle()
        self.distribute()
        self.pile = []

    def distribute(self):
        logger.info(f"distributing cards")
        for i, card in enumerate(self.deck.cards):
            player_index = i % len(self.players)
            self.players[player_index].add_to_hand(card)  # Give card to player
            logger.debug(f"Gave {card} to player {self.players[player_index]}")

    @staticmethod
    def player_give_card_to(player: Player, give: Card, to: Player):
        try:
            receive = player.remove_from_hand(give)
            to.add_to_hand(receive)
        except Exception as e:
            logger.critical(e)
            raise

    @property
    def remaining_players(self):
        active_players = [not player.is_folded for player in self.players].count(True)
        logger.info(f"players count : {active_players}")
        return active_players

    @staticmethod
    def validate_user_input(player: Player, _in: str) -> Card | None:
        if not isinstance(_in, str):
            return PresidentGame.validate_user_input(player, str(_in))

        _card = None
        if _in == "FOLD":
            player.folds()
            _card = None
        for card in player.hand:
            if card.number == _in:
                _card = card
                break
        return _card

    def add_to_pile(self, card: Card) -> None:
        self.pile.append(card)

    def get_pile(self) -> list:
        return self.pile
