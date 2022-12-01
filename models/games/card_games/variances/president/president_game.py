import logging
from typing import Final

from models.games.card_games import Card, CardGame
from rules import PresidentRules
from .president_rankings import PresidentRank


class PresidentGame(CardGame):
    def __init__(self, nb_players=0, nb_ai=3, *players_names, nb_games: int = 0, save=True):
        """ Instantiate a CardGame with President rules and functionalities """
        self.players_limit = PresidentRules.MAX_PLAYERS  # Arbitrary Value
        if PresidentRules.MIN_PLAYERS < nb_players + nb_ai > PresidentRules.MAX_PLAYERS:
            raise ValueError(f"Invalid Total Number of Players to create PresidentGame.")
        super(PresidentGame, self).__init__(nb_players, nb_ai, *players_names, nb_games=nb_games,
                                            save=save)
        self._logger: Final = logging.getLogger(__class__.__name__)
        self._logger.debug("instantiating PresidentGame")

        super().set_game_name(__class__.__name__)  # Override CardGame assignation
        self._revolution = False  # on first game, always False

    def _initialize_game(self):
        """ PresidentGame's inits on top of CardGame's (reset most values, distribute) """
        super(PresidentGame, self)._initialize_game()
        if PresidentRules.NEW_GAME_RESET_REVOLUTION:
            self._revolution = False
        self._winners and self.do_exchanges()

    def do_exchanges(self) -> None:
        """ On start of a new game, after the previous one,
        Players exchange their cards with others according to their ranks"""

        # starting with lowest_rank_player
        self._logger.debug(self._winners)
        for i, player_info in enumerate(self._winners[::-1]):
            player = player_info[0]
            adv = player.rank.advantage
            give_to = self._winners[i][0]
            sentence = f"{player}: {player.rank.rank_name} gives" \
                       f" {'his best ' if adv < 0 else 'no' if not adv else abs(adv)} cards" \
                       f" {'to ' + str(give_to) if adv else ''}"
            self.send_all(sentence)
            for _ in range(abs(adv)):  # give cards according to adv.
                # If neutral, do not trigger
                card = None
                while not card:
                    card = self.player_choose_card_to_give(player)
                self.player_give_to(player, card, give_to)
            # No more card to give
            player.action_required = False  # Actions not required anymore

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
                self.next_player_index = self.get_player_index(player)
        if adv > 0:  # Otherwise choose card to give
            result = player.choose_cards_to_give()
            if result:
                card = result[0]
                player.add_to_hand(card)
        return card

    @property
    def revolution(self):
        return self._revolution

    @property
    def skip_next_player_rule_apply(self):
        """
        This rule apply if current player's play matches cards on the pile and rule is True.
        :return: True if rule applies.
        """
        if not PresidentRules.USE_TA_GUEULE or len(self.pile) <= self.required_cards:
            return False
        pile_comp = self.pile[(self.required_cards * 2)::-1]
        game, player = pile_comp[:self.required_cards], pile_comp[self.required_cards:]
        self._logger.debug(f"{self.players[self.next_player_index]}"
                           f" plays: {player}... comparing to {game}")
        return [game[i] == player[i]
                for i in range(self.required_cards)].count(True) == self.required_cards

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

        self.send_all("#" * 50)
        self.send_all(" ".join(["#" * 15, f"!!! REVOLUTION !!!", "#" * 15]))
        self.send_all("#" * 50)

    def winners(self) -> list[dict]:
        """ get super ranking then append PresidentGame rankings
        :returns: a list of dict containing multiple information on the winners"""

        winners = super().winners()
        for i, winner in enumerate(winners):
            self._logger.info(f"winner {i + 1}: {winner}")
            for player in self.players:
                if player.name == winner['player']:
                    rank = PresidentRank(i + 1, player, len(self.players))
                    winner.setdefault("grade", rank.rank_name)
                    self.send_all(f"{player} has been assigned {rank}")
        return winners

    def card_can_be_played(self, card):
        """ Returns True if the card can be played according to pile and rules """
        return len(self.pile) == 0 or card <= self.pile[-1] and self._revolution \
               or super().card_can_be_played(card)  # resolve by importance

    def _do_play(self, index, player, cards) -> bool:
        """
        Handle PresidentGame variances in rules sets.
        Check if cards are the same power before calling super()._do_play
        <u>Revolution :</u> invert cards power.
        <u>Ta_Gueule :</u>
        - The next player that should've been able to play cannot play (acts like he played)
        - Has no effect if the player is the last standing.
        :returns: True if play is a success, false on any error encountered
        """
        if cards and 1 < len(cards) == [cards[i - 1] == cards[i] for i in
                                        range(1, len(cards))].count(True):
            return False
        super()._do_play(index, player, cards)
        len(cards) == 4 and self.set_revolution()  # if PresidentRules.USE_REVOLUTION
        if self.skip_next_player_rule_apply:
            for _, p in self.next_player:
                if not p:
                    break  # Nothing happens
                self.send_all(''.join(["#" * 20, f"applying TG to {p}", "#" * 20]))
                p.set_played()
                break

        return True  # If nothing has been raised so far, all went good

    def _run_loop(self) -> None:
        """
        In PresidentGame, if there are winners from a previous game, players  must exchange cards
        :param override:
        :param override_test:
        :return:
        """
        if self._run and self._winners:
            self.do_exchanges()  # Do exchanges
        super(PresidentGame, self)._run_loop()

    def to_json(self) -> dict:
        su: dict = super(PresidentGame, self).to_json()
        update = {"revolution": self.revolution}
        if not self._run:
            update.setdefault("president_rules",
                              PresidentRules(len(self.players)).__repr__())

        su.update(update)
        return su
