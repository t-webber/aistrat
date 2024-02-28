import requests
ip="http://137.194.145.251:8080/"
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

getplayer()
R=requests.get(ip+"/view/"+str(player)+'/'+str(token)).json()
print(R)
print(R['map'])
