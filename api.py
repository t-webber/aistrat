import requests
ip="http://localhost:8080"
player=""
token=""

def getplayer():
    global player
    global token
    if ""==player:
        dataplayer=requests.get(ip+"/getToken",timeout=2.5).json()
        print(dataplayer)
        player=dataplayer['player']
        token=dataplayer['token']
    return(player,token)

def movePawn(kind,oldy,oldx,newy,newx) -> bool:
    try: requests.post(ip+"/move/"+player+"/"+kind+"/"+oldy+"/"+oldx+"/"+newy+"/"+newx+"/"+token,timeout=1)
    except: return(False)
    return(True)
    
def buildKind(kind, y, x) -> bool:
    try : print(requests.post(f"{ip}/build/{player}/{y}/{x}/{kind}/{token}", timeout=1).json()) ; return True
    except: return False

def getMap():
    try: carte=requests.get(ip+"/view/"+str(player)+'/'+str(token)).json()
    except: return None
    return carte

def farm(y, x) -> bool:
    try : print(requests.post(f"{ip}/farm/{player}/{y}/{x}/{token}", timeout=1).json()) ; return True
    except: return False

def build(y,x,kind) -> bool:
    try: requests.post("/build/"+player+"/"+y+"/"+x+"/"+kind+"/"+token,timeout=1)
    except: return False
    return True
    
def autofarm() -> bool:
    try : print(requests.post(f"{ip}/autofarm/{player}/{token}", timeout=1).json()) ; return True
    except: return False

def getinfo(y,x):
    return getMap(player,token)[y][x]



getplayer()
R=getMap(player,token)
print(R)
print(R['map'])

