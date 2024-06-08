"""Boîtes noirs pour les unités (château, péon, chevalier) et les piles d'or."""


from __future__ import annotations
from typing import TYPE_CHECKING

from apis import connection, consts

if TYPE_CHECKING:
    from apis.players.players import Player


class Coord:
    """Superclasse pour tous les objets avec des coordonnées."""

    def __init__(self, y: int, x: int):
        """Les coordonnées sont l'ordre(y, x)."""
        self.y = y
        self.x = x

    @property
    def coord(self) -> tuple[int, int]:
        """Obtenir les coordonnées dans un tuple."""
        return (self.y, self.x)


class Enemy(Coord):
    """Superclasse pour les unités ennemies."""

    def __init__(self, y, x, player):
        """Initialise une unité ennemie."""
        super().__init__(y, x)
        self.player = player

class GoldPile(Coord):
    """Classe pour une pile d'or."""

    def __init__(self, y: int, x: int, gold: int, player: Player):
        """Créez une pile d'or avec une certaine quantité d'or."""
        super().__init__(y, x)
        self.gold = gold
        self.used = False

    def reduce(self):
        """Farm une pile d'or."""
        if self.used:
            raise ValueError("Gold is already used.")
        if self.gold <= 0:
            raise ValueError("Gold is empty.")
        self.gold -= 1
        self.used = True
        return self.gold

    def update(self):
        """Mettre à jour la pile d'or pour le changement du virage."""
        self.used = False

    def __str__(self):
        """Renvoie la position de la pile d'or et la quantité d'or."""
        return f"G({self.y}, {self.x})({self.gold})"

    __repr__ = __str__

    def __getitem__(self, key: int):
        """Obtenir la quantité d'or ou les coordonnées."""
        if key == 0:
            return self.y
        if key == 1:
            return self.x
        if key == 2:
            return self.gold
        raise KeyError
        # print(f"Error: key not found for gold: {key}", file=sys.stderr)
        # sys.exit(1)

    def __hash__(self):
        """Effectue le calcul du hash pour les unités."""
        return hash((self.y, self.x, "GOLD"))


class Unit(Coord):
    """Super Boîte noire pour les unités et les châteaux."""

    def __init__(self, y, x, key, enemi_key, player):
        """Créez une unité avec des coordonnées et des clés pour les types d'unités et les unités ennemies."""
        super().__init__(y, x)
        self.y = y
        self.x = x
        self.key = key
        self.enemi_key = enemi_key
        self.player = player
        self.used = True

    # def __getitem__(self, key):
    #     if key in (0, 'y', 'Y'):
    #         return self.y
    #     if key in (1, 'x', 'X'):
    #         return self.x
    #     print(f"Error: key not found: {key}", file=sys.stderr)
    #     sys.exit(1)

    def __hash__(self):
        """Effectue le calcul0 de hash pour les unités."""
        return hash((self.y, self.x, self.key))

class Person(Unit):
    """Super Boîte noire pour les unités (déplacables)."""

    def move(self, y, x):
        """Bouge le péon, et le met en utilisé."""
        # print('pose before', self.y, self.x, 'pos after',y, x)
        if self.used:
            raise ValueError('Person is already used.')
        connection.move(self.key, self.y, self.x, y,
                              x, self.player.id, self.player.token)
        
        self.y = y
        self.x = x
        self.used = True

    def build(self):
        """Build caslte."""
        if self.used:
            raise ValueError("Person is already used.")
        connection.build(consts.CASTLE, self.y, self.x,
                               self.player.id, self.player.token)

        
        self.used = True
        self.player.castles.append(Castle(self.y, self.x, self.player))
        self.player.gold -= Castle.COST


class Pawn(Person):
    """Boîte noire pour les péons."""

    COST = consts.PRICES[consts.PAWN]

    def __init__(self, y, x, player):
        """Initialise un péon."""
        super().__init__(y, x, consts.PAWN, consts.EPAWN, player)

    def farm(self, gold: GoldPile):
        """Farm une pile d'or."""
        if self.used:
            raise ValueError("Person is already used.")
        if gold.used:
            raise ValueError("Gold is already used.")
        if gold.gold <= 0:
            raise ValueError("Gold is empty.")
        # print("or",gold.gold)
        connection.farm(
            self.y, self.x, self.player.id, self.player.token)
        
        self.used = True
        self.player.gold += 1
        gold.reduce()

    def __str__(self):
        """Affiche un péon."""
        return f"P({self.y}, {self.x})"

    __repr__ = __str__


class Knight(Person):
    """Boîte noire pour les chevaliers."""

    COST = consts.PRICES[consts.KNIGHT]

    def __init__(self, y, x, player):
        """Initialise un chevalier."""
        super().__init__(y, x, consts.KNIGHT, consts.EKNIGHT, player)
        self.cible = None  # attribut pour la défense en fonction des chevaliers ennemis

    def __str__(self):
        """Affiche un chevalier."""
        return f"K({self.y}, {self.x})"

    __repr__ = __str__


class Castle(Unit):
    """Boîte noire pour les châteaux."""

    COST = consts.PRICES[consts.CASTLE]

    def __init__(self, y, x, player):
        """Initialise un château."""
        super().__init__(y, x, consts.CASTLE, consts.ECASTLE, player)

    def __str__(self):
        """Affiche un château."""
        return f"C({self.y}, {self.x})"

    __repr__ = __str__
