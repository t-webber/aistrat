"""Fichier qui implémente la class `Player`."""

from apis import connection
from apis.players.player_structure import Player_struct
from player.stages.castles import create_units, build_castle
import player.stages.attack as atk
# import player.stages.decisions as dec
# import player.stages.defense as dfd
from player.stages import peons


class Player(Player_struct):
    """Class pour implémenter les actions d'un joueur."""

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""
        self.reinit_data()

        print("============= BEGin TURN for player", self.id, " =====================")

        self.turn += 1
        self.checks_turn_data()
        self.update_golds()
        self.update_ennemi_data()
        self.update_fog()

        serv = connection.get_gold()[self.id]
        if serv != self.gold:
            raise ValueError(f"wrong gold value: S({serv}) != P({self.gold})")
        # print("CREATE_UNITS\t")

        create_units(self)
        # print("PEONS FUITE\t",'eknights ', self.eknights)
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)
        # print("BUILD CASTLE\t", self.attack + self.defense)
        build_castle(self)

        # print("PEONS FARM\t")
        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # print("EXPLORE\t", self.eknights)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self._knights + self.castles)

        # print("FREE PAWNS\t", self.attack + self.defense)
        atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns)

        # left_defense = dfd.defend(
        #     self.pawns, self.defense, self.eknights, self.castles, self.id, self.token)
        # dfd.agressiv_defense(left_defense, self.epawns,
        #                      self.id, self.token, self.eknights)

        # print(dec.inventory_zones()) #Test pour decisions

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
        self.update_gold_map()

        connection.end_turn(self.id, self.token)
