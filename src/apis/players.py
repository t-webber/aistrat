"""Fichier qui implémente la class `Player`."""

import numpy as np
from apis import connection
from apis.kinds import Pawn, Knight, Castle, GoldPile, Coord
from apis.consts import PLAYER_A, FOG, BEGINING_GOLD
import player.logic.client_logic as cl
from player.stages.castles import create_units, build_castle
import player.stages.attack as atk
# import player.stages.defense as dfd
from player.stages import peons
import player.stages.heatmap as hm

class Player:
    """Class pour implémenter les actions d'un joueur."""

    def __init__(self):
        """Initialise un joueur."""
        self.id, self.token = connection.create_player()
        connection.get_data(self.id, self.token)

        self.turn = 0
        # units
        self.pawns: list[Pawn] = [Pawn(0, 0, self) for _ in range(3)] if self == PLAYER_A else\
                                 [Pawn(connection.size_map()[0] - 1, connection.size_map()[
                                       1] - 1, self) for _ in range(3)]
        self.epawns: list[Pawn] = []
        self.eknights: list[Knight] = []
        self.castles: list[Knight] = []
        self.ecastles: list[Castle] = []
        self.knights: list[Knight] = []
        # resources
        self._golds: list[GoldPile] = [GoldPile(coord[0], coord[1], coord[2], self) for coord in connection.get_kinds(self.id)[
            connection.GOLD]]
        self.gold: int = BEGINING_GOLD
        print(self._golds)
        self.good_gold: list[GoldPile]
        self.bad_gold: list[GoldPile]
        self.good_gold, self.bad_gold = cl.clean_golds(
            self._golds, self.pawns, self.ecastles)
        self.fog: list[GoldPile] = []
        # private
        self._knights: list[Knight] = []
        self._gold_map: list[int | GoldPile] = np.full(connection.size_map(), None)

    def __eq__(self, other):
        """
        Vérifie si deux joueurs sont les mêmes.

        La comparaison peut aussi s'éffecteur avec le nom ('A' ou 'B').
        Voir les constantes dans `api.consts`.
        """
        if isinstance(other, Player):
            return self.id == other.id
        return self.id == other

    def checks_turn_data(self):
        """Vérifie que les données du tour ont bien été récupérées et qu'il n'y a pas eu d'erreur non signalée."""
        connection.get_data(self.id, self.token)
        kinds = connection.get_kinds(self.id)

        check_set_list_coord(self.pawns, kinds[connection.PAWN], "PAWN")
        check_set_list_coord(self.attack + self.defense, kinds[connection.KNIGHT], "KNIGHT")
        check_set_list_coord(self.castles, kinds[connection.CASTLE], "CASTLES")

        # golds = self.good_gold + self.bad_gold
        # golds_items = {}
        # for gold in golds:
        #     y, x = gold.coord
        #     d[y, x] =
        # golds_item = [(item.y, item.x, item.gold) for item in golds]
        # if set(golds_item) != set(kinds[connection.GOLD]):
        #     print(f"gold changed {golds_item} != {kinds[connection.GOLD]}", file=sys.stderr)
        #     raise ValueError

        # if self.gold != connection.get_gold()[self.id]:
        #     print("gold changed", file=sys.stderr)
        #     raise ValueError

    def update_ennemi_data(self):
        """Récupère les données des ennemis."""
        self.epawns = connection.get_kinds(connection.other(self.id))[
            connection.PAWN]
        self.eknights = connection.get_kinds(connection.other(self.id))[
            connection.KNIGHT]
        self.ecastles = connection.get_kinds(connection.other(self.id))[
            connection.CASTLE]

    def update_fog(self):
        """Met à jour les données de brouillard de guerre."""
        self.fog = connection.get_kinds(self.id)[FOG]

    def print_heatmaps(self):
        """Affiche les heatmaps pour le debug"""
        print(self.pawns)
        hm.print_heatmaps(self.pawns, self.knights, self.castles, self.eknights, self.ecastles, self.epawns, self._gold_map, self.id)

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""
        print("DEBUT TURN")

        self.turn += 1
        self.checks_turn_data()
        self.update_ennemi_data()
        self.update_fog()

        create_units(self)
        peons.fuite(self.pawns, self.knights, self.eknights,
                    self.defense)
        build_castle(self)

        # je farm d'abord ce que je vois
        peons.farm(self, self.good_gold)
        # j'explore ensuite dans la direction opposée au spawn
        peons.explore(self, self.knights + self.castles)

        # hm.heatMapMove(self)


        self.update_gold_map()

        self.end_turn()

    def end_turn(self):
        """
        Termine le tour du joueur.

        Toutes les unités sont remise en tant que non utilisées.
        Les réunions de listes sont recalculés.
        """
        for p in self.pawns:
            p.used = False
        for k in self.attack:
            k.used = False
        for k in self.defense:
            k.used = False
        for c in self.castles:
            c.used = False

        self.update_golds()

    def update_golds(self):
        """Met à jour les données des mines d'or."""
        server_golds = connection.get_kinds(self.id)[connection.GOLD]

        golds = self._golds
        self.update_gold_map()
        self._golds = [gold for gold in golds if gold.gold]  # code de goldmon
        servgolds_without_values = [(y, x) for (y, x, _) in server_golds]
        print("BEFORE GOLDS = ", self._golds)

        for gold in self._golds:
            y, x = gold.coord
            v = gold.gold
            if (y, x, v) in server_golds:
                print("Bef = ", server_golds)
                server_golds.remove((y, x, v))
                servgolds_without_values.remove((y, x))
                print("Aft = ", server_golds)
            else:
                try:
                    index = servgolds_without_values.index((y, x))
                    servgolds_without_values.pop(index)
                    server_golds.pop(index)
                except ValueError:
                    pass

        print("GOLDS LEFT = ", server_golds)

        for y, x, gold in server_golds:
            self._golds.append(GoldPile(y, x, gold, self))

        self.good_gold, self.bad_gold = cl.clean_golds(self._golds, self.pawns, self.ecastles)

        for g in self.good_gold:
            g.update()
        for g in self.bad_gold:
            g.update()
        self._knights = self.attack + self.defense
        self._golds = self.good_gold + self.bad_gold

        connection.end_turn(self.id, self.token)

    def update_gold_map(self):
        """Met à jour la carte des or."""
        for coordinate in connection.get_seen_coordinates():
            self._gold_map[coordinate] = 0
        for gold in self._golds:
            coords = gold.coord
            self._gold_map[coords] = gold


def check_set_list_coord(a: list[Coord], b: list[(int, int)], type: str):
    """Vérifie si deux listes sont égales."""
    if set(item.coord for item in a) != set(b):
        print(f"{type} CHANGED: {a} != {b}")
        raise ValueError
