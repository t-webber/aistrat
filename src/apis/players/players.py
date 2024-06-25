
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle
import player.attack as atk
# import player.decisions as dec
import player.defense as dfd
from player import peons
from player.heatmap import heatMapMove, print_heatmaps
import sys
from debug import log_func, pause


class Player(Player_struct):
    """Class pour implémenter les actions d'un joueur."""

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""
        self.reinit_data()

        print(f"============= Begin {self.turn} turn for player {self.id} =====================")

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

        # print('golds', self.good_gold, self.bad_gold)
        create_units(self)
        log_func("fuite")
        peons.fuite(self.pawns, self.knights, self.eknights)
        log_func("castle")
        build_castle(self)
        peons.free_gold(self.pawns, self.bad_gold)
        peons.free_gold(self.pawns, self.good_gold)
        # je farm d'abord ce que je vois
        log_func("farm")
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self.knights + self.castles)

        heatMapMove(self.pawns, self.knights, self.castles, self.epawns, self.eknights, self.ecastles, self._gold_map, self.id)




        self.update_gold_map()

        connection.end_turn(self.id, self.token)
