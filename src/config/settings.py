"""Constantes trouvées expérimentalement."""

DISTANCE_BETWEEN_CASTLES = 3
PAWNS_KNIGHTS_RATIO = 2
CASTLES_RATIO = 2
PRIORITISED_CASTLES_RATIO = 2
DEFEND_KNIGHTS_RATIO = 1.5
PAWNS_OFFSET = 2

assert (PAWNS_OFFSET >= 1 and isinstance(PAWNS_OFFSET, int))
assert (PAWNS_KNIGHTS_RATIO >= 1)
assert (PRIORITISED_CASTLES_RATIO >= 1)
assert (DEFEND_KNIGHTS_RATIO >= 1)
