"""
fichier qui implémente la classe Player
"""

import sys
from api import connection
import player.logic.client_logic as cl
import player.stages.castles as builder
import player.stages.attack as atk
import player.stages.defense as dfd
import player.stages.peons as peons


class Player:
    """
    class pour implémenter les actions d'un joueur
    """

    def __init__(self):
        self.id, self.token = connection.create_player()
        # units
        self.pawns = set()
        self.epawns = set()
        self.eknights = set()
        self.castles = set()
        self.ecastles = set()
        self.attack = set()
        self.defense = set()
        # resources
        self.gold = 0
        self.good_gold = set()
        self.bad_gold = set()
        self.fog = set()

    @property
    def golds(self):
        " recupérer toutes les piles d'or "
        return self.good_gold + self.bad_gold

    @property
    def knights(self):
        " recupérer tous les chevaliers "
        return self.attack + self.defense

    def checks_turn_data(self):
        """
        vérifie que les données du tour ont bien été récupérées
        et qu'il n'y a pas eu d'erreur non signalée
        """
        kinds = connection.get_kinds(self.id)

        if self.pawns != set(kinds[connection.PAWN]):
            print("pawns changed", file=sys.stderr)
            sys.exit(1)

        if self.epawns != set(kinds[connection.EPAWN]):
            print("epawns changed", file=sys.stderr)
            sys.exit(1)

        if self.attack + self.defense != set(kinds[connection.KNIGHT]):
            print("knights changed", file=sys.stderr)
            sys.exit(1)

        if self.eknights != set(kinds[connection.EKNIGHT]):
            print("eknights changed", file=sys.stderr)
            sys.exit(1)

        if self.castles != set(kinds[connection.CASTLE]):
            print("castles changed", file=sys.stderr)
            sys.exit(1)

        if self.ecastles != set(kinds[connection.ECASTLE]):
            print("ecastles changed", file=sys.stderr)
            sys.exit(1)

        if self.good_gold + self.bad_gold != len(set(kinds[connection.GOLD])):
            print("gold changed", file=sys.stderr)
            sys.exit(1)

        if self.fog != set(kinds[connection.FOG]):
            print("fog changed", file=sys.stderr)
            sys.exit(1)

        if self.defense != cl.defense_knights[self.id]:
            print("defense changed", file=sys.stderr)
            sys.exit(1)

        if self.gold != connection.get_gold()[self.id]:
            print("gold changed", file=sys.stderr)
            sys.exit(1)

        if (self.good_gold, self.bad_gold) != cl.clean_golds(self.golds, self.pawns, self.ecastles):
            print("gold cleaning changed", file=sys.stderr)
            sys.exit(1)

    def check_attack_defense(self):
        """ 
        vérifie que les chevaliers sont bien attribués à l'attaque ou à la défense, 
        et les attribuent dans le cas échéant
        """
        for d in self.defense:
            if d not in self.knights():
                self.defense.remove(d)
            else:
                self.knights.remove(d)

    def next_turn(self):
        " joue le prochain tour pour le joueur "

        self.check_attack_defense()

        builder.create_pawns(self.castles, self.id, self.token,
                             self.eknights, self.knights, self.gold, self.defense,
                             len(self.golds), len(self.pawns), len(self.fog))
        peons.fuite(self.pawns, self.knights, self.eknights,
                    self.defense, self.id, self.token)

        builder.check_build(self.pawns, self.castles,
                            self.id, self.token, self.gold, self.eknights)
        # je farm d'abord ce que je vois
        peons.farm(self.pawns, self.id, self.token,
                   self.good_gold, self.eknights, self.ecastles)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self.pawns, self.id, self.token, self.eknights,
                      self.ecastles, self.knights+self.castles, self.bad_gold)

        atk.free_pawn(self.knights, self.id, self.token,
                      self.eknights, self.epawns)

        left_defense = dfd.defend(
            self.pawns, self.defense, self.eknights, self.castles, self.id, self.token)
        dfd.agressiv_defense(left_defense, self.epawns,
                             self.id, self.token, self.eknights)

        copy_knights = self.knights.copy()
        while copy_knights:
            a = len(copy_knights)
            atk.hunt(copy_knights, self.epawns,
                     self.eknights, self.id, self.token)
            atk.destroy_castle(copy_knights, self.ecastles,
                               self.eknights, self.id, self.token)
            if len(copy_knights) == a:
                break
