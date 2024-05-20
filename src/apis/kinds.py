"""Boîtes noirs pour les unités (château, péon, chevalier) et les piles d'or."""

from apis import connection


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


class GoldPile(Coord):
    """Classe pour une pile d'or."""

    def __init__(self, y: int, x: int, gold: int):
        """Créez une pile d'or avec une certaine quantité d'or."""
        super().__init__(y, x)
        self.gold = gold
        self.used = False

    def reduce(self):
        """Farm une pile d'or."""
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
        self.used = False

    # def __getitem__(self, key):
    #     if key in (0, 'y', 'Y'):
    #         return self.y
    #     if key in (1, 'x', 'X'):
    #         return self.x
    #     print(f"Error: key not found: {key}", file=sys.stderr)
    #     sys.exit(1)


class Person(Unit):
    """Super Boîte noire pour les unités (déplacables)."""

    def move(self, y, x):
        """Bouge le péon, et le met en utilisé."""
        if self.used:
            return False

        res = connection.move(self.key, self.y, self.x, y,
                              x, self.player.id, self.player.token)
        if res:
            self.y = y
            self.x = x
            self.used = True
        return res


class Pawn(Person):
    """Boîte noire pour les péons."""

    COST = 5

    def __init__(self, y, x, player):
        """Initialise un péon."""
        super().__init__(y, x, "C", "C2", player)

    def farm(self):
        """Farm une pile d'or."""
        res = connection.farm(
            self.y, self.x, self.player.id, self.player.token)
        if res:
            self.used = True
        return res

    def __str__(self):
        """Affiche un péon."""
        return f"P({self.y}, {self.x})"

    __repr__ = __str__


class Knight(Person):
    """Boîte noire pour les chevaliers."""

    COST = 10

    def __init__(self, y, x, player):
        """Initialise un chevalier."""
        super().__init__(y, x, 'M', 'M2', player)

    def __str__(self):
        """Affiche un chevalier."""
        return f"K({self.y}, {self.x})"

    __repr__ = __str__


class Castle(Unit):
    """Boîte noire pour les châteaux."""

    COST = 15

    def __init__(self, y, x, player):
        """Initialise un château."""
        super().__init__(y, x, 'B', 'B2', player)

    def __str__(self):
        """Affiche un château."""
        return f"C({self.y}, {self.x})"

    __repr__ = __str__
