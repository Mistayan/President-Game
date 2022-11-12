import logging
from typing import Final

from models.games.card_game import CardGame

from models import Card
from models.rankings import PresidentRank
from rules import PresidentRules


class PresidentGame(CardGame):
    def __init__(self, nb_players=3, nb_ai=0, *players_names, nb_games: int = 0, save=True):
        """ Instantiate a CardGame with President rules and functionalities """
        self._logger: Final = logging.getLogger(__class__.__name__)
        if 3 < nb_players + nb_ai > 6:
            raise ValueError(f"Invalid Total Number of Players to create PresidentGame. 3-6")
        self._pile = []  # Pre-instantiating pile to avoid null/abstract pointer
        self.players = []
        super().__init__(nb_players, nb_ai, *players_names, nb_games=nb_games, save=save)
        self.game_name = __class__.__name__  # Override name
        self._revolution = False

    def _initialize_game(self):
        """ PresidentGame's inits on top of CardGame's (reset most values, distribute) """
        super(PresidentGame, self)._initialize_game()
        if PresidentRules.NEW_GAME_RESET_REVOLUTION:
            self._revolution = False

    def do_exchanges(self) -> None:
        """ On start of a new game, after the previous one,
        Players exchange their cards with others according to their ranks"""

        # starting with lowest_rank_player
        self._logger.debug(self._winners)
        for i, player_info in enumerate(self._winners[::-1]):
            player = player_info[0]
            adv = player.rank.advantage
            give_to = self._winners[i][0]
            sentence = f"{player} gives {'his best ' if adv < 0 else ''}" \
                       f"{'no' if not adv else abs(adv)}" \
                       f" cards {'to ' + str(give_to) if adv else ''}"
            print(sentence)
            for _ in range(abs(adv)):  # give cards according to adv.
                # If neutral, do not trigger
                card = None
                while not card:
                    card = self.player_choose_card_to_give(player)
                self.player_give_card_to(player, card, give_to)

    def player_choose_card_to_give(self, player) -> Card:
        """
        According to player's rank's advantage,
        :param player: player that have to choose a card to give to another player
        :return: the chosen Card
        """
        adv = player.rank.advantage
        card = None
        if adv < 0:  # Give best card if negative advantage
            card = player.hand[-1]
            if player.rank.rank_name == "Troufion":
                self.last_playing_player_index = self.get_player_index(player)
        if adv > 0:  # Otherwise choose card to give
            result = player.play(1)
            if result:
                card = result[0]
                player.add_to_hand(card)
        return card

    @property
    def revolution(self):
        return self._revolution

    def set_revolution(self):
        """ VARIANCE OF THE GAME RULES
        REVOLUTION is a rule that allows players to play 4 times the same card
        in order to reverse cards power.

        It can be cancelled if a player plays another 4 cards on top of the previous revolution,
        or either on his turn, later on.

        Inspired by the French revolution, yet to become True.
        """
        if not PresidentRules.USE_REVOLUTION:
            return
        self._revolution, self.VALUES = not self._revolution, self.VALUES[::-1]

        print("#" * 50)
        print(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        print("#" * 50)

    def winners(self) -> list[dict]:
        """ get super ranking then append PresidentGame rankings
        :returns: a list of dict containing multiple information on the winners"""

        winners = super().winners()
        for i, winner in enumerate(winners):
            self._logger.info(f"winner {i + 1}: {winner}")
            for player in self.players:
                if player.name == winner['player']:
                    winner.setdefault("grade",
                                      PresidentRank(i + 1, player, len(self.players)).rank_name)
        return winners

    def card_can_be_played(self, card):
        """ Returns True if the card can be played according to pile and rules """
        return not self.pile or (self.pile[-1] <= card and not self._revolution
                                 or self.pile[-1] >= card and self._revolution)

    def _do_play(self, index, player, cards) -> bool:
        self.set_revolution() if len(cards) == 4 else None  # REVOLUTION ?
        return super()._do_play(index, player, cards)

    def _run_loop(self, override=None, override_test=False) -> None:
        super(PresidentGame, self)._run_loop(override, override_test)
        if self._run:
            self.do_exchanges()  # Do exchanges
