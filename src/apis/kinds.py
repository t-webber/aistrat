import sys
from apis import connection


class Coord:
    """ (y, x) """


class Unit:
    """
    Super class for all allies units
    """

    def __init__(self, y, x, key, enemi_key, cost, player):
        self.y = y
        self.x = x
        self.key = key
        self.enemi_key = enemi_key
        self.cost = cost
        self.player = player
        self.moved = False

    def move(self, y, x):
        res = connection.move(self.key, self.y, self.x, y,
                              x, self.player.id, self.player.token)
        if res:
            self.y = y
            self.x = x
        return res


class Pawn(Unit):

    def __init__(self, y, x, player):
        super().__init__(y, x, "C", "C2", 5, player)


class Knight(Unit):

    def __init__(self, y, x, player):
        super().__init__(y, x, 'M', 'M2', 10, player)


class Castle(Unit):

    def __init__(self, y, x, player):
        super().__init__(y, x, 'B', 'B2', 15, player)


CASTLE = "B"
KNIGHT = "M"
GOLD = 'G'
EKNIGHT = "M2"
EPAWN = "C2"
FOG = "fog"
ECASTLE = "B2"
