# -*- coding: utf-8 -*-
"""
Created by: Mistayan
Project: President-Game
IDE: PyCharm
Creation-date: 11/19/22
"""
import logging
from typing import Final

from models.games.card_games import Card, CardGame
from rules import PresidentRules, GameRules
from .president_rankings import PresidentRank


class PresidentGame(CardGame):
    """ Variance of a Card Game """

    def __init__(self, nb_players=0, nb_ai=3, *players_names, nb_games: int = 0, save=True):
        """ Instantiate a CardGame with President rules and functionalities """
        super(PresidentGame, self).__init__(nb_players, nb_ai, *players_names, nb_games=nb_games,
                                            save=save)

        self._logger.debug("instantiating PresidentGame")
        self.game_rules = PresidentRules(nb_players + nb_ai)  # Add variances rules to rules-sets
        if self.game_rules.min_players < nb_players + nb_ai > self.game_rules.max_players:
            raise ValueError("Invalid Total Number of Players to create PresidentGame.")
        self._logger: Final = logging.getLogger(__class__.__name__)

        super().set_game_name(__class__.__name__)  # Override CardGame assignation
        self._revolution = False  # on first game, always False

    def _initialize_game(self):
        """ PresidentGame's inits on top of CardGame's (reset most values, distribute) """
        super()._initialize_game()
        if self.game_rules.new_game_reset_revolution:
            self._revolution = False
        if self._winners:
            self.do_exchanges()

    def do_exchanges(self) -> None:
        """ On start of a new game, after the previous one,
        Players exchange their cards with others according to their ranks"""

        # starting with lowest_rank_player
        self._logger.debug(self._winners)
        for i, player_info in enumerate(self._winners[::-1]):
            player = player_info[0]
            if player.rank:
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
            player.is_action_required = False  # Actions not required anymore

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
        """ returns state of revolution in actual game """
        return self._revolution

    @property
    def skip_next_player_rule_apply(self):
        """
        This rule apply if current player's play matches
         cards on the pile and rule is True.
        :return: True if rule applies.
        """
        if not self.game_rules.use_ta_gueule or len(self.pile) <= self.required_cards:
            return False
        pile_comp = self.pile[(self.required_cards * 2)::-1]
        game, player = pile_comp[:self.required_cards], pile_comp[self.required_cards:]
        self._logger.debug("%s plays: %s... comparing to %s",
                           self.players[self.next_player_index], player, game)
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
        if not self.game_rules.use_revolution:
            return
        self._revolution, self.game_rules.VALUES = not self._revolution, self.game_rules.VALUES[::-1]

        self.send_all("#" * 50)
        self.send_all(" ".join(["#" * 15, "!!! REVOLUTION !!!", "#" * 15]))
        self.send_all("#" * 50)

    def winners(self) -> list[dict]:
        """ get super ranking then append PresidentGame rankings
        :returns: a list of dict containing multiple information on the winners"""

        winners = super().winners()
        for i, winner in enumerate(winners):
            i = i + 1
            self._logger.info("winner %d: %s", i, winner)
            for player in self.players:
                if player.name == winner['player']:
                    rank = PresidentRank(i, player, len(self.players))
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
            for _, p in self._next_player:
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
        super()._run_loop()

    def _update_game_rules(self, param: GameRules | dict):
        self._logger.info(f"Changing rules with {param}")
        super()._update_game_rules(param)
        self.game_rules.NEW_GAME_RESET_REVOLUTION = param.get('new_game_reset_revolution',
                                                              self.game_rules.NEW_GAME_RESET_REVOLUTION)
        self.game_rules.QUEEN_OF_HEART_STARTS = param.get('queen_of_heart_start_first_game',
                                                          self.game_rules.QUEEN_OF_HEART_STARTS)
        self.game_rules.LOSER_CAN_PLAY = param.get('last_player_can_play_until_over', self.game_rules.LOSER_CAN_PLAY)
        self.game_rules.WAIT_NEXT_ROUND_IF_FOLD = param.get('fold_means_played',
                                                            self.game_rules.WAIT_NEXT_ROUND_IF_FOLD)
        self.game_rules.PLAYING_BEST_CARD_END_ROUND = param.get('playing_best_card_end_round',
                                                                self.game_rules.PLAYING_BEST_CARD_END_ROUND)
        self._logger.debug(f"afterwards : {self.game_rules.__dict__()}")

    def to_json(self) -> dict:
        """ Serialize PresidentGame for communications"""
        su: dict = super().to_json()
        update = {"revolution": self.revolution}
        #        if not self._run:
        #            update.update("game_rules",
        #                              PresidentRules(len(self.players)).__repr__())

        su.update(update)
        return su
