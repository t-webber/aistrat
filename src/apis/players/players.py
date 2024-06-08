"""Fichier qui implémente la class `Player`."""

import numpy as np
from apis.players.player_structure import Player_struct
from apis import connection
from apis.kinds import Pawn, Knight, GoldPile, Coord, Enemy, Unit
from apis.consts import FOG, BEGINING_GOLD
import player.logic.client_logic as cl
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
        self.update_ennemi_data()
        self.update_fog()

        # print("CREATE_UNITS\t", self.pawns)

        create_units(self)
        print("PEONS FUITE\t", self.defense)
        peons.fuite(self.pawns, self.attack, self.eknights,
                    self.defense)
        # print("BUILD CASTLE\t", self.attack + self.defense)
        build_castle(self)

        # print("PEONS FARM\t", self.pawns)
        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # print("bf EXPLORE\t", self.pawns)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self._knights + self.castles)

        print("FREE PAWNS\t", self.attack + self.defense)
        atk.free_pawn(self.attack + self.defense, self.eknights, self.epawns)

        # left_defense = dfd.defend(
        #     self.pawns, self.defense, self.eknights, self.castles, self.id, self.token)
        # dfd.agressiv_defense(left_defense, self.epawns,
        #                      self.id, self.token, self.eknights)

        #print(dec.inventory_zones()) #Test pour decisions

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