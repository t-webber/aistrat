import requests
ip="http://localhost:8080"
player=""
token=""

def getplayer():
    global player
    global token
    if player=="":
        L=requests.get(ip+"/getToken",timeout=2.5).json()
        print(L)
        player=L['player']
        token=L['token']
    return(player,token)

def movePawn(player,kind,oldy,oldx,newy,newx,token) -> bool:
    try: requests.post(ip+"/move/"+player+"/"+kind+"/"+oldy+"/"+oldx+"/"+newy+"/"+newx+"/"+token,timeout=1)
    except: return(False)
    return(True)
    
def buildKind(player, kind, y, x, token) -> bool:
    try : print(requests.post(f"{ip}/build/{player}/{y}/{x}/{kind}/{token}", timeout=1).json()) ; return True
    except: return False

def getMap(player,token):
    try: R=requests.get(ip+"/view/"+str(player)+'/'+str(token)).json()
    except: return None
    return R

def farm(player, y, x, token) -> bool:
    try : print(requests.post(f"{ip}/farm/{player}/{y}/{x}/{token}", timeout=1).json()) ; return True
    except: return False

def build(player,y,x,kind,token) -> bool:
    try: requests.post("/build/"+player+"/"+y+"/"+x+"/"+kind+"/"+token,timeout=1)
    except: return False
    return True
    
def autofarm(player, token) -> bool:
    try : print(requests.post(f"{ip}/autofarm/{player}/{token}", timeout=1).json()) ; return True
    except: return False

getplayer()
R=getMap(player,token)
print(R)
print(R['map'])

