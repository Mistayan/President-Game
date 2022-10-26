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
        if len(players_names) > number_of_players:
            raise IndexError(f"Too many names for Player count")
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
