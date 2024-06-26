
"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle, castle_flee
import player.attack as atk
# import player.decisions as dec
import player.defense as dfd
from player import peons
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

        pause(self.id)

        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")

        # print('golds', self.good_gold, self.bad_gold)
        create_units(self)

        log_func("castle_flee")
        castle_flee(self.castles, self.defense + self.attack, self.eknights, self)
        log_func("fuite")
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)

        log_func("castle")
        build_castle(self)
        peons.free_gold(self.pawns, self.bad_gold)
        peons.free_gold(self.pawns, self.good_gold)
        # je farm d'abord ce que je vois
        log_func("farm")
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        log_func("explore")
        peons.explore(self, self._knights + self.castles)
        # atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns, self.ecastles)
        log_func("defend")
        dfd.defend(self.pawns, self.defense, self.eknights, self.castles)
        # dfd.agressiv_defense(self.defense, self.epawns, self.eknights, self.ecastles)
        last_len = None
        log_func("sync atk")
        atk.sync_atk(self.attack, self.eknights, self.epawns, self)
        while (length := [k for k in self.attack if not k.used]):
            log_func("hunt")
            atk.hunt(self.attack, self.epawns, self.eknights)
            log_func("destroy")
            atk.destroy_castle(self.attack + self.defense, self.ecastles, self.eknights)
            if last_len == length:
                break

            last_len = length
        log_func("explore_knight")
        peons.explore_knight(self, self.pawns + self.castles)

        log_func("second create unit")
        create_units(self)
        self.update_gold_map()

        connection.end_turn(self.id, self.token)
