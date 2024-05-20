"""
Blackboxes for units
"""

from apis import connection


class Coord:
    """ (y, x) """

    def __init__(self, y: int, x: int):
        self.y = y
        self.x = x

    @property
    def coord(self) -> tuple[int, int]:
        """
        Get the coordinates in a tuple
        """
        return (self.y, self.x)


class GoldPile(Coord):
    """ (y, x, gold) """

    def __init__(self, y: int, x: int, gold: int):
        super().__init__(y, x)
        self.gold = gold
        self.used = False

    def reduce(self):
        """ farm a gold pile """
        self.gold -= 1
        self.used = True
        return self.gold

    def update(self):
        """ update gold pile """
        self.used = False

    def __str__(self):
        return f"G({self.y}, {self.x})"

    __repr__ = __str__

    def __getitem__(self, key: int):
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
    """
    Super class for all units and castles
    """

    def __init__(self, y, x, key, enemi_key, player):
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

    @property
    def coord(self):
        """
        Renvoie les coordonnées de l'unité
        """
        return (self.y, self.x)


class Person(Unit):
    """
    Super class for a movable unit
    """

    def move(self, y, x):
        """
        move a pawn to a new position and set it to moved
        """
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
    """"
    Pawn class
    """

    COST = 5

    def __init__(self, y, x, player):
        super().__init__(y, x, "C", "C2", player)

    def farm(self):
        """
        farm a gold pile
        """
        res = connection.farm(
            self.y, self.x, self.player.id, self.player.token)
        if res:
            self.used = True
        return res

    def __str__(self):
        return f"P({self.y}, {self.x})"

    __repr__ = __str__


class Knight(Person):
    """"
    Knight class
    """

    COST = 10

    def __init__(self, y, x, player):
        super().__init__(y, x, 'M', 'M2', player)

    def __str__(self):
        return f"K({self.y}, {self.x})"

    __repr__ = __str__


class Castle(Unit):
    """
    Castle class
    """

    COST = 15

    def __init__(self, y, x, player):
        super().__init__(y, x, 'B', 'B2', player)

    def __str__(self):
        return f"C({self.y}, {self.x})"

    __repr__ = __str__
