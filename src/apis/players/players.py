
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle
import player.attack as atk
# import player.decisions as dec
# import player.defense as dfd
from player import peons


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

        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")

        create_units(self)
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)
        build_castle(self)

        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self._knights + self.castles)

        atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns, self.ecastles)

        last_len = None

        while (length := [k for k in self.attack if not k.used]):

            # print("HUNT ATK\t", self.pawns)
            atk.hunt(self.attack, self.epawns,
                     self.eknights)
            # print("DESTROY CASTLE\t", self.pawns)
            atk.destroy_castle(self.attack, self.ecastles,
                               self.eknights)
            if last_len == length:
                break

            last_len = length
        peons.explore_knight(self, self.pawns + self.castles)
        self.update_gold_map()

        connection.end_turn(self.id, self.token)
