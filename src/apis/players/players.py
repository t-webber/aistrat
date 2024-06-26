
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle
import player.attack as atk
# import player.decisions as dec
import player.defense as dfd
from player import peons
import sys


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

        if self == "A" and len(sys.argv) >= 3 and sys.argv[2] == "debug":
            input("Press enter to continue...")

        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")

        create_units(self)
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)
        build_castle(self)
        peons.free_gold(self.pawns, self.bad_gold)
        peons.free_gold(self.pawns, self.good_gold)
        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self._knights + self.castles)
        # atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns, self.ecastles)
        dfd.defend(self.pawns, self.defense, self.eknights, self.castles)
        # left_defense = dfd.eknight_based_defense ( defense, eknights, castles, token)
        dfd.agressiv_defense(self.defense, self.epawns, self.eknights, self.ecastles)
        last_len = None
        atk.sync_atk(self.attack, self.eknights, self.epawns)
        while (length := [k for k in self.attack if not k.used]):

            atk.hunt(self.attack, self.epawns, self.eknights)
            atk.destroy_castle(self.attack, self.ecastles, self.eknights)
            if last_len == length:
                break

            last_len = length

        peons.explore_knight(self, self.pawns + self.castles)

        self.update_gold_map()

        connection.end_turn(self.id, self.token)
