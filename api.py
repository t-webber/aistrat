import requests
ip="http://localhost:8080"
player=""
token=""
taille=[0,0]
turn_data = []

PAWN = "C"
CASTLE = "B"
KNIGHT = "M"

def endTurn():
    try: requests.get(f"{ip}/endturn/{player}/{token}",timeout=1)
    except ValueError: 
        print("Erreur move", ValueError)
        return(False)
    return(True)

def createPlayer():
    global player
    global token
    if ""==player:
        dataplayer=requests.get(ip+"/getToken",timeout=2.5).json()
        print(dataplayer)
        player=dataplayer['player']
        token=dataplayer['token']
    return(player,token)

def move(kind,oldy,oldx,newy,newx) -> bool:
    try: requests.get(f"{ip}/move/{player}/{kind}/{oldy}/{oldx}/{newy}/{newx}/{token}",timeout=1)
    except ValueError: 
        print("Erreur move", ValueError)
        return(False)
    return(True)
    
def build(kind, y, x) -> bool:
    try: print(requests.get(f"{ip}/build/{player}/{y}/{x}/{kind}/{token}", timeout=1).json()); return True
    except: return False

def getData():
    global turn_data
    try: res = requests.get(f"{ip}/view/{player}/{token}")
    except: return False
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

def farm(y, x) -> bool:
    try: print(requests.get(f"{ip}/farm/{player}/{y}/{x}/{token}", timeout=1).json()); return True
    except: return False
   
def autoFarm() -> bool:
    try: print(requests.get(f"{ip}/autofarm/{player}/{token}", timeout=1).json()); return True
    except: return False

def getInfo(y,x): 
    return turn_data[y][x]

class Coord: pass

def getKinds() -> dict[str, list[Coord]]:
    result = { PAWN: [], CASTLE: [], KNIGHT: [] }
    carte = getMap()
    for y in range(len(carte)):
        for x in range(len(carte[y])):
            try:d = carte[y][x][player]         
            except:continue  
            if d[PAWN]:
                for _ in range(d[PAWN]): result[PAWN].append((y, x))
            if d[CASTLE]: 
                for _ in range(d[CASTLE]): result[CASTLE].append((y, x))
            if d[KNIGHT]:
                for _ in range(d[KNIGHT]): result[KNIGHT].append((y, x))
    return result

def getMoves(y,x):
    INITIAL_MAP = getMap()
    taille = [len(INITIAL_MAP), len(INITIAL_MAP[0])]
    moves=[]
    for i in [-1,1]:
        if taille[0]>y+i>=0:
            moves.append((y+i,x))
        if taille[1]>x+i>=0:
            moves.append((y,x+i))
    return moves


def init():
    return createPlayer()[0]

#print(getData())
#INITIAL_MAP=getMap()
#taille=[len(INITIAL_MAP), len(INITIAL_MAP[0])]

if __name__ == "__main__":
    createPlayer()
    getData()
    R=getMap()
    print(R[0])
    move("C",0,0,1,0)
    move("C",0,1,1,1)
    getData()
    R=getMap()
    print(R)