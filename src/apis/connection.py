"""API pour communiquer avec le serveur."""

import numpy as np
import requests
from apis.kinds import Coord, Unit
from apis.consts import PAWN, CASTLE, KNIGHT, GOLD, EKNIGHT, EPAWN, ECASTLE

IP = "http://localhost:8080"
TIME_OUT = 0.01


MAP_SIZE = None

turn_data = {}


def init(ip: str):
    """Initialise l'API avec la bonne IP pour le serveur."""
    global IP
    IP = ip


def end_turn(player_id: str, token: str):
    """Fin du tour du joueur."""
    try:
        requests.get(
            f"{IP}/endturn/{player_id}/{token}", timeout=TIME_OUT)
    except:
        return False
    return True


def create_player():
    """Cree le joueur."""
    dataplayer = requests.get(IP + "/getToken", timeout=TIME_OUT).json()
    player_id = dataplayer['player']
    token = dataplayer['token']
    return player_id, token


def move(kind: str, oldy: int, oldx: int, newy: int, newx: int, player_id: str, token: str) -> bool:
    """Essaie de bouger une unité."""
    try:
        requests.get(
            f"{IP}/move/{player_id}/{kind}/{oldy}/{oldx}/{newy}/{newx}/{token}", timeout=TIME_OUT)
    except:
        return False
    return True


def build(kind: str, y: int, x: int, player_id: str, token: str) -> bool:
    """Contruit une unité de type `kind` en (y,x)."""
    try:
        requests.get(
            f"{IP}/build/{player_id}/{y}/{x}/{kind}/{token}", timeout=TIME_OUT)
        return True
    except:
        return False


def get_data(player_id: str, token: str) -> bool:
    """
    Reçoit toutes les informations pour le tour.

    Les données sont stockées dans une variable globale pour ne pas faire appel à cet fonction plus que nécessaire.
    """
    global turn_data
    try:
        res = requests.get(
            f"{IP}/view/{player_id}/{token}", timeout=TIME_OUT)
    except:
        return False
    turn_data = res.json()
    return True


def get_map() -> list[list[dict]]:
    """Renvoie la carte du jeu en brut sous forme de tableau de dictionnaires."""
    return turn_data["map"]


def size_map() -> tuple[int, int]:
    """Renvoie la taille de la carte de jeu."""
    global MAP_SIZE
    if MAP_SIZE is None:
        initial_map = get_map()
        print(initial_map[0][0])
        MAP_SIZE = (len(initial_map), len(initial_map[0]))
    return MAP_SIZE


def current_player() -> list:
    """Renvoie le joueur dont c'est le tour."""
    return turn_data["player"]


def get_gold() -> list:
    """Renvoie l'argent qu'on possède."""
    return turn_data["gold"]


def get_score():
    """Renvoie le score de la partie."""
    return turn_data["score"]


def get_winner() -> str:
    """Renvoie le gagnant de la partie."""
    return turn_data["winner"]


def farm(y: int, x: int, player_id: str, token: str) -> bool:
    """Fait récolter de l'argent au péon en (y, x)."""
    try:
        requests.get(
            f"{IP}/farm/{player_id}/{y}/{x}/{token}", timeout=TIME_OUT)
        return True
    except:
        return False


def auto_farm(player_id, token) -> bool:
    """Fait récolter de l'argent à tous les péons."""
    try:
        requests.get(
            f"{IP}/autofarm/{player_id}/{token}", timeout=TIME_OUT)
        return True
    except:
        return False


def get_info(y: int, x: int) -> list:
    """Récupère une info particulière sur le tour."""
    return turn_data[y][x]


def other(player_id: str) -> str:
    """Renvoie l'autre joueur par rapport à `player_id`."""
    if player_id == 'A':
        return 'B'
    return 'A'


def get_kinds(player_id: str) -> dict[str, list[(int, int)]]:
    """Renvoie la liste des coordonées de toutes les unitées présentes sur la carte."""
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


def get_moves(y: int, x: int) -> list[tuple]:
    """Fonction renvoyant toutes les cases disponibles autours d'une case donnée."""
    moves = []
    for i in [-1, 1]:
        if size_map()[0] > y + i >= 0:
            moves.append((y + i, x))
        if size_map()[1] > x + i >= 0:
            moves.append((y, x + i))
    return moves


def get_seen_coordinates():
    """Fait la liste des cases visibles par le joueur."""
    carte = get_map()
    results = []
    for (y, line) in enumerate(carte):
        for (x, col) in enumerate(line):
            if col != {}:
                results.append((y, x))
    return results


def get_visible(units: list[Unit]) -> list[int]:
    """Renvoie une carte avec des nombres donnant le "nombre de fois" que chaque case est visible."""
    carte = np.zeros(size_map())
    for boy in units:
        for y in [boy.y + k for k in [-2, -1, 0, 1, 2]]:
            for x in [boy.x + k for k in [-2, -1, 0, 1, 2]]:
                if (0 <= (y) < len(carte)) and (0 <= (x) < len(carte[0])):
                    carte[y][x] += 1
    return carte


def add_visible(carte, unit: Coord) -> list[int]:
    """Ajoute la vision d'une unité à la carte."""
    for y in [unit[0] + k for k in [-2, -1, 0, 1, 2]]:
        for x in [unit[1] + k for k in [-2, -1, 0, 1, 2]]:
            if (0 <= (y) < len(carte)) and (0 <= (x) < len(carte[0])):
                carte[y][x] += 1
    return carte


def get_eknights(y: int, x: int) -> list[tuple]:
    """Renvoie la liste des chevaliers présents sur une case donnée."""
    d = get_map()[y][x][current_player()]
    result = []
    if d[KNIGHT]:
        for _ in range(d[KNIGHT]):
            result.append((y, x))
    return result
