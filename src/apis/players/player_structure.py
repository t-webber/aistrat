"""Fichier qui implémente la class `Player`."""

import numpy as np
from apis import connection
from apis.kinds import Pawn, Knight, Castle, GoldPile, Enemy, Unit
from config.consts import FOG, BEGINING_GOLD
import logic.client_logic as cl


class Player_struct:
    """Class pour implémenter les actions d'un joueur."""

    def __init__(self):
        """Initialise un joueur."""
        self.id, self.token = connection.create_player()
        connection.get_data(self.id, self.token)
        self.height, self.width = connection.size_map()
        self.turn = 0
        # units
        self.pawns: list[Pawn] = [Pawn(y, x, self) for y, x in connection.get_kinds(self.id)[connection.PAWN]]
        self.epawns: list[Enemy] = []
        self.eknights: list[Enemy] = []
        self.castles: list[Castle] = [Castle(y, x, self) for y, x in connection.get_kinds(self.id)[connection.CASTLE]]
        self.ecastles: list[Pawn] = []
        self.attack: list[Knight] = [Knight(y, x, self) for y, x in connection.get_kinds(self.id)[connection.KNIGHT]]
        self.defense: list[Knight] = []
        # resources
        self._golds: list[GoldPile] = [GoldPile(coord[0], coord[1], coord[2], self) for coord in connection.get_kinds(self.id)[
            connection.GOLD]]
        self._golds_total = connection.get_kinds(self.id)[connection.GOLD]
        self._golds_total_without_values = [(y, x) for (y, x, _) in self._golds_total]
        self.average_gold = sum([i**2 for i in range(13)]) / 12
        self.golds_plot_not_seen = 15 - sum([self.decomposition(gold[2]) for gold in self._golds_total])
        self.gold: int = connection.get_gold()[self.id]
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
        Voir les constantes dans `config.consts`.
        """
        if isinstance(other, Player_struct):
            return self.id == other.id
        return self.id == other

    def checks_turn_data(self):
        """Vérifie que les données du tour ont bien été récupérées et qu'il n'y a pas eu d'erreur non signalée."""
        connection.get_data(self.id, self.token)
        kinds = connection.get_kinds(self.id)

        self.check_set_list_coord(self.pawns, kinds[connection.PAWN], "PAWN")
        self.check_set_list_coord(self.attack + self.defense, kinds[connection.KNIGHT], "KNIGHT")
        self.check_set_list_coord(self.castles, kinds[connection.CASTLE], "CASTLES")

    def update_ennemi_data(self):
        """Récupère les données des ennemis."""
        other_player = connection.other(self.id)
        self.epawns = [Enemy(*x, other_player) for x in connection.get_kinds(connection.other(self.id))[
            connection.PAWN]]
        self.eknights = [Enemy(*x, other_player) for x in connection.get_kinds(connection.other(self.id))[
            connection.KNIGHT]]
        self.ecastles = [Enemy(*x, other_player) for x in connection.get_kinds(connection.other(self.id))[
            connection.CASTLE]]

    def update_fog(self):
        """Met à jour les données de brouillard de guerre."""
        self.fog = connection.get_kinds(self.id)[FOG]

    def reinit_data(self):
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

    def update_golds(self):
        """Met à jour les données des mines d'or."""
        server_golds = connection.get_kinds(self.id)[connection.GOLD]
        # self.update_gold_map()
        servgolds_without_values = [(y, x) for (y, x, _) in server_golds]
        # self.update_total_gold(server_golds, servgolds_without_values)
        updated_golds = []
        print(server_golds)
        print(servgolds_without_values)
        for gold in self._golds:
            y, x = gold.coord
            v = gold.gold
            if not v:
                print('coucou2',gold)
                continue
            if (y, x, v) in server_golds:
                server_golds.remove((y, x, v))
                servgolds_without_values.remove((y, x))
                updated_golds.append(gold)
            elif (y, x) in servgolds_without_values:
                index = servgolds_without_values.index((y, x))
                _, _, new_v = server_golds[index]
                gold.gold = new_v
                updated_golds.append(gold)
                server_golds.remove((y, x, new_v))
                servgolds_without_values.pop(index)
            elif gold in self.fog:
                updated_golds.append(gold)

        for (y, x, v) in server_golds:
            updated_golds.append(GoldPile(y, x, v, self))

        updated_golds.sort()

        if not (set(server_golds) <= set(gold.y, gold.x, gold.gold) for gold in updated_golds):
            raise ValueError(f"gold changed {updated_golds} != {server_golds}")

        self.good_gold, self.bad_gold = cl.clean_golds(updated_golds, self.pawns, self.ecastles)

        for g in self.good_gold:
            g.update()
            if g.gold <= 0:
                self.good_gold.remove(g.gold)
        for g in self.bad_gold:
            g.update()
            if g.gold <= 0:
                self.bad_gold.remove(g.gold)

        self._knights = self.attack + self.defense
        self._golds = self.good_gold + self.bad_gold

    def update_gold_map(self):
        """Met à jour la carte des or."""
        for coordinate in connection.get_seen_coordinates():
            self._gold_map[coordinate] = 0
        for gold in self._golds:
            coords = gold.coord
            self._gold_map[coords] = gold

    def update_total_gold(self, server_golds: list[(int, int, int)], server_golds_without_values: list[(int, int)]):
        """Met à jour ce qu'on sait des golds à l'état de jeu initial."""
        for i, (y, x) in enumerate(server_golds_without_values):
            if (y, x) not in self._golds_total_without_values and (self.height - 1 - y, self.width - 1 - x) not in self._golds_total_without_values:
                self._golds_total.append(server_golds[i])
                self._golds_total_without_values.append((y, x))
                self.golds_plot_not_seen -= self.decomposition(server_golds[i][2])

    def estimation_gold(self):
        """Estime le nombre de golds restant."""
        return sum([gold.gold for gold in self._golds]) + max(0, self.golds_plot_not_seen) * self.average_gold

    def decomposition(self, n):
        """Renvoie 1 si n est un carré parfait et 2 sinon."""
        if (n**0.5).is_integer():
            return 1
        else:
            return 2

    def check_set_list_coord(self, client_units: list[Unit], server_units: list[(int, int)], instance: str):
        """Vérifie si deux listes sont égales."""

        client = client_units.copy()
        server = server_units.copy()

        for unit in client:
            if unit.coord in server:
                server.remove(unit.coord)
            else:
                client_units.remove(unit)
                print(f"{instance} {unit} was killed")
        if server:
            raise ValueError(f"{instance} changed: server {server_units} != client {client_units}")
