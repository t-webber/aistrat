""" API to communicate between client and serve """

import requests
IP = "http://localhost:8080"
TIME_OUT = 0.05
PAWN = "C"
CASTLE = "B"
KNIGHT = "M"
GOLD = 'G'
taille = [0, 0]
turn_data = []


def end_turn(player, token):
    """ End the turn of the player """
    try:
        requests.get(
            f"{IP}/endturn/{player}/{token}", timeout=TIME_OUT)
    except ValueError:
        print("Erreur move", ValueError)
        return False
    return True


def create_player():
    """ Create the player """
    dataplayer = requests.get(IP+"/getToken", timeout=TIME_OUT).json()
    print(dataplayer)
    player = dataplayer['player']
    token = dataplayer['token']
    return player, token


def move(kind, oldy, oldx, newy, newx, player, token) -> bool:
    """ Try moving """
    try:
        requests.get(
            f"{IP}/move/{player}/{kind}/{oldy}/{oldx}/{newy}/{newx}/{token}", timeout=TIME_OUT)
    except ValueError:
        print("Erreur move", ValueError)
        return False
    return True


def build(kind, y, x, player, token) -> bool:
    """ Build a castle at (y,x) """
    try:
        print(requests.get(
            f"{IP}/build/{player}/{y}/{x}/{kind}/{token}", timeout=TIME_OUT).json())
        return True
    except:
        return False


def get_data(player, token):
    """ get all data for the turn """
    global turn_data
    try:
        res = requests.get(f"{IP}/view/{player}/{token}", timeout=TIME_OUT)
    except:
        return False
    turn_data = res.json()
    return True


def get_map():
    return turn_data["map"]


INITIAL_MAP = get_map()
MAP_SIZE = (len(INITIAL_MAP), len(INITIAL_MAP[0]))


def size_map():
    return MAP_SIZE


def current_player():
    return turn_data["player"]


def get_gold():
    return turn_data["gold"]


def get_score():
    return turn_data["score"]


def get_winner():
    return turn_data["winner"]


def farm(y, x, player, token) -> bool:
    """ Farm a peon on (y, x) """
    try:
        print(requests.get(
            f"{IP}/farm/{player}/{y}/{x}/{token}", timeout=TIME_OUT).json())
        return True
    except:
        return False


def auto_farm(player, token) -> bool:
    """ Farm all peons """
    try:
        print(requests.get(
            f"{IP}/autofarm/{player}/{token}", timeout=TIME_OUT).json())
        return True
    except:
        return False


def get_info(y, x):
    return turn_data[y][x]


class Coord:
    """ (y, x) """


def get_kinds(player) -> dict[str, list[Coord]]:
    """ returns the list of the coordinates of all the present units on the map """
    result = {PAWN: [], CASTLE: [], KNIGHT: [], GOLD: [], 'fog': []}
    carte = get_map()
    for (y, line) in enumerate(carte):
        for (x, col) in enumerate(line):
            if col == {}:
                result['fog'].append((y, x))
            else:
                d = col[player]
                if d[PAWN]:
                    for _ in range(d[PAWN]):
                        result[PAWN].append((y, x))
                if d[CASTLE]:
                    for _ in range(d[CASTLE]):
                        result[CASTLE].append((y, x))
                if d[KNIGHT]:
                    for _ in range(d[KNIGHT]):
                        result[KNIGHT].append((y, x))

                g = carte[y][x][GOLD]
                if g:
                    result[GOLD].append((y, x, g))
    return result


def get_moves(y, x):
    """ Function to get the avaible cells around the current position """
    moves = []
    for i in [-1, 1]:
        if MAP_SIZE[0] > y+i >= 0:
            moves.append((y+i, x))
        if MAP_SIZE[1] > x+i >= 0:
            moves.append((y, x+i))
    return moves


if __name__ == "__main__":
    current_player, current_token = create_player()
    get_data(current_player, current_token)
    R = get_map()
    print(R[0])
    move("C", 0, 0, 1, 0, current_player, current_token)
    move("C", 0, 1, 1, 1, current_player, current_token)
    get_data(current_player, current_token)
    R = get_map()
    print(R)
