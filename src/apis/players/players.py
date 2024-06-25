
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle
import player.attack as atk
# import player.decisions as dec
# import player.defense as dfd
from player import peons
from player.heatmap import heatMapMove, print_heatmaps

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

        
        # if self.turn%10 == 0:
        #     print_heatmaps(self.pawns, self.knights, self.castles, self.eknights, self.ecastles, self.epawns, self._gold_map, self.id)

        
        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")

        create_units(self)
        peons.fuite(self.pawns, self.knights, self.eknights)
        build_castle(self)

        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self.knights + self.castles)

        heatMapMove(self.pawns, self.knights, self.castles, self.epawns, self.eknights, self.ecastles, self._gold_map, self.id)
        
        self.update_gold_map()

        connection.end_turn(self.id, self.token)
