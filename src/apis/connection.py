""" API to communicate between client and serve """
import numpy as np
import requests
from apis.kinds import Coord
from apis.consts import PAWN, CASTLE, KNIGHT, GOLD, EKNIGHT, EPAWN, ECASTLE

IP = "http://localhost:8080"
TIME_OUT = 0.01


MAP_SIZE = None

turn_data = {}


def init(ip: str):
    """ Initialise l'API """
    global IP
    IP = ip


def end_turn(player_id, token):
    """fin du tour du joueur """
    try:
        requests.get(
            f"{IP}/endturn/{player_id}/{token}", timeout=TIME_OUT)
    except:
        return False
    return True


def create_player():
    """ Cree le joueur """
    dataplayer = requests.get(IP+"/getToken", timeout=TIME_OUT).json()
    player_id = dataplayer['player']
    token = dataplayer['token']
    return player_id, token


def move(kind, oldy, oldx, newy, newx, player_id, token) -> bool:
    """ essaie de bouger """
    try:
        requests.get(
            f"{IP}/move/{player_id}/{kind}/{oldy}/{oldx}/{newy}/{newx}/{token}", timeout=TIME_OUT)
    except:
        return False
    return True


def build(kind, y, x, player_id, token) -> bool:
    """ construit une unité de type "kind" en (y,x) """
    try:
        requests.get(
            f"{IP}/build/{player_id}/{y}/{x}/{kind}/{token}", timeout=TIME_OUT).json()
        return True
    except:
        return False


def get_data(player_id: str, token: str):
    """ reçoit toutes les information pour le tour """
    global turn_data
    try:
        res = requests.get(
            f"{IP}/view/{player_id}/{token}", timeout=TIME_OUT)
    except:
        return False
    turn_data = res.json()
    return True


def get_map():
    '''Renvoie la carte du jeu en brut sous forme de tableau de dictionnaires'''
    return turn_data["map"]


def size_map():
    '''Renvoie la taille de la carte de jeu'''
    global MAP_SIZE
    if MAP_SIZE is None:
        initial_map = get_map()
        MAP_SIZE = (len(initial_map), len(initial_map[0]))
    return MAP_SIZE


def current_player():
    '''Renvoie le joueur dont c'est le tour'''
    return turn_data["player_id"]


def get_gold():
    '''Renvoie l'argent qu'on possède'''
    return turn_data["gold"]


def get_score():
    '''Renvoie le score de la partie'''
    return turn_data["score"]


def get_winner():
    '''Renvoie le gagnant de la partie'''
    return turn_data["winner"]


def farm(y, x, player_id, token) -> bool:
    """ fait récolter de l'argent au péon en (y, x) """
    try:
        (requests.get(
            f"{IP}/farm/{player_id}/{y}/{x}/{token}", timeout=TIME_OUT).json())
        return True
    except:
        return False


def auto_farm(player_id, token) -> bool:
    """ fait récolter de l'argent à tous les péons """
    try:
        (requests.get(
            f"{IP}/autofarm/{player_id}/{token}", timeout=TIME_OUT).json())
        return True
    except:
        return False


def get_info(y, x):
    '''Récupère une info particulière sur le tour'''
    return turn_data[y][x]


def other(player_id: str):
    '''Renvoie l'autre joueur par rapport à player_id'''
    if player_id == 'A':
        return 'B'
    return 'A'


def get_kinds(player_id: str) -> dict[str, list[Coord]]:
    """ Renvoie la liste des coordonées de toutes les unitées présentes sur la carte """
    result = {PAWN: [], CASTLE: [], KNIGHT: [],
              GOLD: [], 'fog': [], EKNIGHT: [], EPAWN: [], ECASTLE: []}
    carte = get_map()
    for (y, line) in enumerate(carte):
        for (x, col) in enumerate(line):
            if col == {}:
                result['fog'].append((y, x))
            else:
                d = col[player_id]
                if d[PAWN]:
                    for _ in range(d[PAWN]):
                        result[PAWN].append((y, x))
                if d[CASTLE]:
                    for _ in range(d[CASTLE]):
                        result[CASTLE].append((y, x))
                if d[KNIGHT]:
                    for _ in range(d[KNIGHT]):
                        result[KNIGHT].append((y, x))

                d2 = col[other(player_id)]
                if d2[KNIGHT]:
                    for _ in range(d2[KNIGHT]):
                        result[EKNIGHT].append((y, x))

                if d2[PAWN]:
                    for _ in range(d2[PAWN]):
                        result[EPAWN].append((y, x))

                if d2[CASTLE]:
                    for _ in range(d2[CASTLE]):
                        result[ECASTLE].append((y, x))
                g = col[GOLD]
                if g:
                    result[GOLD].append((y, x, g))
    return result


def get_moves(y, x):
    """ Fonction renvoyant toutes les cases disponibles autours d'une case donnée """
    moves = []
    for i in [-1, 1]:
        if size_map()[0] > y+i >= 0:
            moves.append((y+i, x))
        if size_map()[1] > x+i >= 0:
            moves.append((y, x+i))
    return moves


def get_visible(units):
    '''Renvoie à partir d'une fausse carte de la taille de la carte de jeu et des pions
    une carte avec des nombres donnant le "nombre de fois" que la case est visible'''
    carte = np.zeros(size_map())
    for boy in units:
        for y in [boy[0]+k for k in [-2, -1, 0, 1, 2]]:
            for x in [boy[1]+k for k in [-2, -1, 0, 1, 2]]:
                if (0 <= (y) < len(carte)) and (0 <= (x) < len(carte[0])):
                    carte[y][x] += 1
    return carte


def add_visible(carte, unit):
    '''Ajoute la vision d'une unité à la carte'''
    for y in [unit[0]+k for k in [-2, -1, 0, 1, 2]]:
        for x in [unit[1]+k for k in [-2, -1, 0, 1, 2]]:
            if (0 <= (y) < len(carte)) and (0 <= (x) < len(carte[0])):
                carte[y][x] += 1
    return carte


def get_defenders(y, x):
    ''' Renvoie la liste des chevaliers présents sur une case donnée '''
    d = get_map()[y][x][current_player()]
    result = []
    if d[KNIGHT]:
        for _ in range(d[KNIGHT]):
            result.append((y, x))
    return result
