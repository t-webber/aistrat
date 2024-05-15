"""
Blackboxes for units
"""

from apis import connection
import sys

class Coord:
    """ (y, x) """

X = 1
Y = 0

class Unit:
    """
    Super class for all units and castles
    """

    def __init__(self, y, x, key, enemi_key, cost, player):
        self.y = y
        self.x = x
        self.key = key
        self.enemi_key = enemi_key
        self.cost = cost
        self.player = player
        self.used = False

    def __getitem__(self, key):
        if key in (0, 'y', 'Y'):
            return self.y
        if key in (1, 'x', 'X'):
            return self.x
        print("Error: key not found", file=sys.stderr)
        sys.exit(1)



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

    def __init__(self, y, x, player):
        super().__init__(y, x, "C", "C2", 5, player)

    def farm(self):
        """
        farm a gold pile
        """
        res = connection.farm(self.y, self.x, self.player.id, self.player.token)
        if res:
            self.used = True
        return res

class Knight(Person):
    """"
    Knight class
    """

    def __init__(self, y, x, player):
        super().__init__(y, x, 'M', 'M2', 10, player)


class Castle(Unit):
    """
    Castle class
    """

    def __init__(self, y, x, player):
        super().__init__(y, x, 'B', 'B2', 15, player)
