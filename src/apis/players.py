"""
fichier qui implémente la classe Player
"""

import sys
from apis import connection
from apis.kinds import Pawn, Knight, Castle, GoldPile
from apis.consts import PLAYER_A, FOG
import player.logic.client_logic as cl
from player.stages.castles import create_units, build_castle
import player.stages.attack as atk
import player.stages.defense as dfd
from player.stages import peons


class Player:
    """
    class pour implémenter les actions d'un joueur
    """

    def __init__(self):
        self.id, self.token = connection.create_player()
        connection.get_data(self.id, self.token)

        self.turn = 0
        # units
        self.pawns: list[Pawn] = [Pawn(0, 0, self) for _ in range(3)] if self == PLAYER_A else\
                                 [Pawn(connection.size_map()[0], connection.size_map()[
                                       1], self) for _ in range(3)]
        self.epawns: list[Pawn] = []
        self.eknights: list[Knight] = []
        self.castles: list[Knight] = []
        self.ecastles: list[Castle] = []
        self.attack: list[Knight] = []
        self.defense: list[Knight] = []
        # resources
        self.gold: int = 0
        self._golds: list[GoldPile] = [GoldPile(coord[0], coord[1], coord[2]) for coord in connection.get_kinds(self.id)[
            connection.GOLD]]
        print(self._golds)
        self.good_gold: list[GoldPile]
        self.bad_gold: list[GoldPile]
        self.good_gold, self.bad_gold = cl.clean_golds(
            self._golds, self.pawns, self.ecastles)
        self.fog: list[GoldPile] = []
        # private
        self._knights: list[Knight] = []

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.id == other.id
        return self.id == other

    def checks_turn_data(self):
        """
        vérifie que les données du tour ont bien été récupérées
        et qu'il n'y a pas eu d'erreur non signalée
        """
        connection.get_data(self.id, self.token)
        kinds = connection.get_kinds(self.id)

        if self.pawns != set(kinds[connection.PAWN]):
            print("pawns changed", file=sys.stderr)
            # sys.exit(1)

        if self.epawns != set(kinds[connection.EPAWN]):
            print("epawns changed", file=sys.stderr)
            # sys.exit(1)

        if self.attack.extend(self.defense) != set(kinds[connection.KNIGHT]):
            print("knights changed", file=sys.stderr)
            # sys.exit(1)

        if self.eknights != set(kinds[connection.EKNIGHT]):
            print("eknights changed", file=sys.stderr)
            # sys.exit(1)

        if self.castles != set(kinds[connection.CASTLE]):
            print("castles changed", file=sys.stderr)
            # sys.exit(1)

        if self.ecastles != set(kinds[connection.ECASTLE]):
            print("ecastles changed", file=sys.stderr)
            # sys.exit(1)

        if self.good_gold.extend(self.bad_gold) != len(set(kinds[connection.GOLD])):
            print("gold changed", file=sys.stderr)
            # sys.exit(1)

        if self.fog != set(kinds[FOG]):
            print("fog changed", file=sys.stderr)
            # sys.exit(1)

        if self.defense != cl.defense_knights[self.id]:
            print("defense changed", file=sys.stderr)
            # sys.exit(1)

        if self.gold != connection.get_gold()[self.id]:
            print("gold changed", file=sys.stderr)
            # sys.exit(1)

        if (self.good_gold, self.bad_gold) != cl.clean_golds(self._golds, self.pawns, self.ecastles):
            print("gold cleaning changed", file=sys.stderr)
            # sys.exit(1)

        for gold in self.good_gold:
            gold.update()
        for gold in self.bad_gold:
            gold.update()

    # def check_attack_defense(self):
    #     """
    #     vérifie que les chevaliers sont bien attribués à l'attaque
    #     ou à la défense, et les attribuent dans le cas échéant
    #     """
    #     for d in self.defense:
    #         if d not in self._knights:
    #             self.defense.remove(d)
    #         else:
    #             self.knights.remove(d)

    def update(self):
        """
        met à jour les données du joueur
        """
        self._knights = self.attack + self.defense
        self._golds = self.good_gold + self.bad_gold

    def next_turn(self):
        " joue le prochain tour pour le joueur "
        self.turn += 1
        self.update()
        self.checks_turn_data()
        # self.check_attack_defense()

        create_units(self)

        peons.fuite(self.pawns, self._knights, self.eknights,
                    self.defense)

        build_castle(self)
        # je farm d'abord ce que je vois
        peons.farm(self.pawns, self.id, self.token,
                   self.good_gold, self.eknights, self.ecastles)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self.pawns, self.id, self.token, self.eknights,
                      self.ecastles, self._knights + self.castles, self.bad_gold)

        atk.free_pawn(self._knights, self.eknights, self.epawns)

        left_defense = dfd.defend(
            self.pawns, self.defense, self.eknights, self.castles, self.id, self.token)
        dfd.agressiv_defense(left_defense, self.epawns,
                             self.id, self.token, self.eknights)

        copy_knights = self._knights.copy()
        while copy_knights:
            a = len(copy_knights)
            atk.hunt(copy_knights, self.epawns,
                     self.eknights)
            atk.destroy_castle(copy_knights, self.ecastles,
                               self.eknights)
            if len(copy_knights) == a:
                break

        self.end_turn()

    def end_turn(self):
        """
        Termine le tour du joueur
        """
        for p in self.pawns:
            p.used = False
        for k in self.attack:
            k.used = False
        for k in self.defense:
            k.used = False
        for c in self.castles:
            c.used = False

        connection.end_turn(self.id, self.token)
