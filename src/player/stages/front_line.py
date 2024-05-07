import api



#front_line['A'] is for the player A and front_line['B'] is for the player B
front_line = { 'A':[], 'B':[]}

is_full = {'A':False, 'B':False}


def update_front(player, knights):
    '''
    met le front à jour avec les potentielles pertes
    '''
    for row in range(api.map_size[0]):
        front_line[player][row][1] = 0
    for (row, colomn) in knights:
        if front_line[player][row][0] == colomn:
            front_line[player][row][1] += 1



def create_front(player):
    '''
    créer le front pour un joueur, en positionnant l'origine du front a 4 cases du bord
    '''
    start_front = api.map_size[1]-5
    if player == 'A':
        start_front = 4
    for row in range(api.map_size[0]):
        front_line[player].append ([start_front, 0])


def in_line(knight, player):
    '''
    renvoit un booléen indiquant si un soldat est sur la ligne de front ou non
    '''
    (row, colomn) = knight
    return (front_line[player][row][0] == colomn)

def broken_line(player):
    '''
    renvoit un bouléen pour savoir si la ligne de front contient un trou
    '''

    for row in range(api.map_size[0]):
        if front_line[player][row][1] == 0:
            return True
    return False

def blitzkrieg(knights, player, token):
    '''
    ordonne à tous les soldats d'avancer sans réfléchir
    '''

    direction = 1
    if player == 'B':
        direction = -1
    
    for (row, colomn) in knights:
        if -1 < colomn + direction < api.map_size[1]:
            api.move(api.KNIGHT, row, colomn, row,
                  colomn + direction, player, token)
    


def direction(player):
    '''
    renvoit la direction d'attaque pour un joueur
    '''
    if player == 'B':
        return -1
    return 1



def move_to_line(knights, player, token):
    '''
    déplace les soldats n'étant pas sur la ligne de front vers cette dernière
    '''
    for (row, colomn) in knights:
        if -1 < colomn + direction(player) < api.map_size[1] and not in_line((row, colomn), player):
            api.move(api.KNIGHT, row, colomn, row,
                  colomn + direction(player), player, token)
            if in_line((row, colomn+direction(player)), player):
                front_line[player][row][1] += 1

def equilibrate(knights, player, token):
    '''
    répartit les soldats sur la front de manière naîve et gloutonne (on se déplace si il y a moins de monde juste a côté)
    '''
    has_moved = False
    for (row, colomn) in knights:
        if in_line((row, colomn), player):
            if row > 0 and front_line[player][row][1] > front_line[player][row-1][1] :
                api.move(api.KNIGHT, row, colomn, row-1,
                colomn, player, token)
                front_line[player][row-1][1] += 1
                front_line[player][row][1] -= 1
                has_moved = True

            elif row < api.map_size[0]-1 and front_line[player][row][1] > front_line[player][row+1][1]:
                api.move(api.KNIGHT, row, colomn, row+1,
                colomn, player, token)
                front_line[player][row+1][1] += 1
                front_line[player][row][1] -= 1
                has_moved = True
    return has_moved

def is_full_update(player):
    for row in range(api.map_size[0]):
        if front_line[player][row][1] == 0:
            return False
    return True



def advance(knights, eknights, player, token):
    '''
    fait avancer les soldats de la ligne de front s'il n'y a pas de soldats ennemis sur le chemin
    '''
    for (row, colomn) in eknights:
        if colomn == front_line[player][0][1]+direction(player):
            return False
    for (row, colomn) in knights:
        api.move(api.KNIGHT, row, colomn, row,
        colomn+direction(player), player, token)
        front_line[player][row][0] += direction(player)
    return True
