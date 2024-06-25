
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle
import player.attack as atk
# import player.decisions as dec
import player.defense as dfd
from player import peons
import time


class Player(Player_struct):
    """Class pour implémenter les actions d'un joueur."""

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""
        self.reinit_data()

        print("============= Begin Turn for player", self.id, " =====================")

        self.turn += 1
        self.checks_turn_data()
        self.update_golds()
        self.update_ennemi_data()
        self.update_fog()

        # input("Press enter to continue...")

        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")

        create_units(self)
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)
        build_castle(self)

        peons.free_gold(self.pawns, self.bad_gold)
        available_good_golds = peons.free_gold(self.pawns, self.good_gold)

        # je farm d'abord ce que je vois
        peons.farm(self, available_good_golds)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self._knights + self.castles)

        # atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns, self.ecastles)

        dfd.defend(self.pawns, self.defense, self.eknights, self.castles)
        #left_defense = dfd.eknight_based_defense ( defense, eknights, castles, token)
        print('defense:', self.defense)
        dfd.agressiv_defense(self.defense, self.epawns, self.eknights, self.ecastles)
        print('defense2:', self.defense)

        last_len = None

        while (length := [k for k in self.attack if not k.used]):

            atk.hunt(self.attack, self.epawns,
                     self.eknights)
            atk.destroy_castle(self.attack, self.ecastles,
                               self.eknights)
            if last_len == length:
                break

            last_len = length
        peons.explore_knight(self, self.pawns + self.castles)
        self.update_gold_map()

        connection.end_turn(self.id, self.token)
