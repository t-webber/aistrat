import requests
ip = "http://localhost:8080"
player = ""
token = ""
taille = [0, 0]
turn_data = []
time_out = 0.05
PAWN = "C"
CASTLE = "B"
KNIGHT = "M"
GOLD = 'G'


def endTurn(player, token):
    try:
        requests.get(f"{ip}/endturn/{player}/{token}", timeout=time_out)
    except ValueError:
        print("Erreur move", ValueError)
        return (False)
    return (True)


def createPlayer():
    # global player
    # global token
    if "" == "":
        dataplayer = requests.get(ip+"/getToken", timeout=time_out).json()
        print(dataplayer)
        player = dataplayer['player']
        token = dataplayer['token']
    else:
        print('deja pris')
    return (player, token)


def move(kind, oldy, oldx, newy, newx, player, token) -> bool:
    try:
        requests.get(
            f"{ip}/move/{player}/{kind}/{oldy}/{oldx}/{newy}/{newx}/{token}", timeout=time_out)
    except ValueError:
        print("Erreur move", ValueError)
        return (False)
    return (True)


def build(kind, y, x, player, token) -> bool:
    try:
        print(requests.get(
            f"{ip}/build/{player}/{y}/{x}/{kind}/{token}", timeout=time_out).json())
        return True
    except:
        return False


def getData(player, token):
    global turn_data
    try:
        res = requests.get(f"{ip}/view/{player}/{token}", timeout=time_out)
    except:
        return False
    turn_data = res.json()
    return True


def getMap():
    return turn_data["map"]


def currentPlayer():
    return turn_data["player"]


def getGold():
    return turn_data["gold"]


def getScore():
    return turn_data["score"]


def getWinner():
    return turn_data["winner"]


def farm(y, x, player, token) -> bool:
    try:
        print(requests.get(
            f"{ip}/farm/{player}/{y}/{x}/{token}", timeout=time_out).json())
        return True
    except:
        return False


def autoFarm(player, token) -> bool:
    try:
        print(requests.get(
            f"{ip}/autofarm/{player}/{token}", timeout=time_out).json())
        return True
    except:
        return False


def getInfo(y, x):
    return turn_data[y][x]


class Coord:
    pass


def getKinds(player) -> dict[str, list[Coord]]:
    result = {PAWN: [], CASTLE: [], KNIGHT: [], GOLD: [], 'fog': []}
    carte = getMap()
    for y in range(len(carte)):
        for x in range(len(carte[y])):
            if carte[y][x] == {}:
                result['fog'].append((y, x))
            else:
                d = carte[y][x][player]
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
                if g: result[GOLD].append((y, x, g))
    return result


def getMoves(y, x):
    INITIAL_MAP = getMap()
    taille = [len(INITIAL_MAP), len(INITIAL_MAP[0])]
    moves = []
    for i in [-1, 1]:
        if taille[0] > y+i >= 0:
            moves.append((y+i, x))
        if taille[1] > x+i >= 0:
            moves.append((y, x+i))
    return moves


def init():
    return createPlayer()[0]

# print(getData())
# INITIAL_MAP=getMap()
# taille=[len(INITIAL_MAP), len(INITIAL_MAP[0])]


if __name__ == "__main__":
    createPlayer()
    getData()
    R = getMap()
    print(R[0])
    move("C", 0, 0, 1, 0)
    move("C", 0, 1, 1, 1)
    getData()
    R = getMap()
    print(R)
