import requests
ip="http://localhost:8080"
player=""
token=""
taille=[0,0]

PAWN = "C"
CASTLE = "B"
KNIGHT = "M"

def endTurn():
    try: requests.get(f"{ip}/endturn/{player}/{token}",timeout=1)
    except ValueError: 
        print("Erreur move", ValueError)
        return(False)
    return(True)

def getPlayer():
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

def getMap():
    try: carte=requests.get(f"{ip}/view/{player}/{token}").json()
    except: return None
    return carte["map"]

def farm(y, x) -> bool:
    try: print(requests.get(f"{ip}/farm/{player}/{y}/{x}/{token}", timeout=1).json()); return True
    except: return False
   
def autoFarm() -> bool:
    try: print(requests.get(f"{ip}/autofarm/{player}/{token}", timeout=1).json()); return True
    except: return False

def getInfo(y,x): 
    return getMap(player,token)[y][x]

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
    moves=[]
    for i in [-1,1]:
        if taille[0]>y+i>=0:
            moves.append((y+i,x))
        if taille[1]>x+i>=0:
            moves.append((y,x+i))
    return moves

getPlayer()
M=getMap()
taille=[len(M),len(M)[0]]

if __name__ == "__main__":
    getPlayer()
    R=getMap()
    print(R['map'])
    move("C",0,0,1,0)
    move("C",0,1,1,1)
    R=getMap()
    print(R['map'])