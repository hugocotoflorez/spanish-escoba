from baraja_class import get_baraja,barajar
from colorama import Fore
import random

colors = [b for a,b in Fore.__dict__.items() if a not in ['RESET','BLACK','GREEN','WHITE','GREY']]

#initialize new baraja
baraja = get_baraja()
#merge the baraja
barajar(baraja)
mesa = []
ultima_llevada = ''
while True:
    try:
        jugadores = []
        for _ in range(int(input('Numero de jugadores: '))):
            while True:
                name = input('Numbre: ')
                if not name in jugadores:
                    jugadores.append(name)
                    break
                else:
                    print('Nombre ya usado!')
        while True:
            try:
                max_points = int(input('Puntos para ganar la partida: '))
                break
            except Exception:
                continue
        break
    except Exception:
        continue
    
random.shuffle(jugadores)

game_dict = {player:{'mano':[],'escobas':0,'points':0,'cards':[],'color':colors.pop(random.randint(0,len(colors)-1))} for player in jugadores}

def print_mesa():
    print(Fore.GREEN+'*'*12+' Mesa '+'*'*12+Fore.RESET)
    if mesa:
        print('\n'.join([f'{i.name}({i.number})' for i in mesa]))
    else:
        print('Mesa vacia')
    print(Fore.GREEN+'*'*30+'\n'+Fore.RESET)
    
    
def sumer(arr,n):
    match=[]
    for i,e in enumerate(arr):
        num = e.number
        if num == n: match.append([e])
        elif num >n: continue
        elif num==0: continue
        else:
            s = sumer(arr[i+1:],n-num)
            if s:
                for c in s: c.append(e)
                match+=s
    return match

def get_bigger(stats,t):
    keys = []
    for k,a in stats.items():
        if not keys: keys.append(k)
        elif stats[keys[0]] < a: keys=[k]
        elif stats[keys[0]] == a: keys.append(k)
    print(t,stats,keys)
    return keys
        

def get_cards_amount_winner():
    stats = {a:len(b['cards']) for a,b in game_dict.items()}
    return (x:=get_bigger(stats,'cartas')),stats[x[0]]
    
def get_oros_amount_winner():
    stats = {a:len([c for c in b['cards'] if c.palo=='oros']) for a,b in game_dict.items()}
    return (x:=get_bigger(stats,'orors')),stats[x[0]]    

def get_sietes_amount_winner():
    stats = {a:len([c for c in b['cards'] if c.number==7]) for a,b in game_dict.items()}
    return (x:=get_bigger(stats,'sietes')),stats[x[0]]

def get_points(name,stats):
    p = []
    total = 0
    for a in range(stats['escobas']):
        p.append('\tEscoba +1') 
        total +=1
    for a in stats['cards']:
        if a.name == '\t7 de oros':
            p.append('velo +1')   
            total +=1  
    
    if name in pt1[0]:
        if pt1[1] == 40:
            p.append('\t todas las cartas +10')
            total +=10
        else:
            p.append('\tcartas +1')
            total+=1
    
    if name in pt3[0]:
        if pt1[1] == 4:
            p.append('\t 4 sietes +3')
            total +=3
        else:
            p.append('\tsietes +1')
            total+=1
    
    if name in pt2[0]:
        if pt1[1] == 10:
            p.append('\t todas los oros +10')
            total +=3
        else:
            p.append('\toros +1')
            total+=1
            
    p.append(f'\tTotal: {total}')   
    game_dict[name]['points']+=total    
    return p 
while True:
    jugadores.append(jugadores.pop(0))
    for a in game_dict.keys():
        for b in game_dict[a]['cards']:
            baraja.append(b)
        game_dict[a]['cards'] = list()
    barajar(baraja)
    print('-'*30)
    print(f'{Fore.WHITE}Reparte: {jugadores[-1]}. Orden: {" -> ".join(jugadores)}{Fore.RESET}')
    print('-'*30)

    for _ in range(4):
        mesa.append(baraja.pop(0))
    s = sumer(mesa,15)
    if s:
        for a in s:
            if len(a) == 4:
                print_mesa()
                print('\n'+f'{Fore.GREEN} ESCOBA INICIAL de {jugadores[-1]}')
                for c in a:
                    game_dict[jugadores[-1]]['cards'].append(c)
                    mesa.remove(c)
    loops = 12//len(jugadores)
    for t in range(loops,0,-1):
        print('\n'+Fore.GREEN+'-'*30)
        print('Repartiendo...\t'+f'{t} turnos restantes')
        print('-'*30+Fore.RESET)
        for a in game_dict.keys():
            for _ in range(3):
                game_dict[a]['mano'].append(baraja.pop(0))
            
        
        for turno in range(3):
            for player in jugadores:
                print('\n')
                print_mesa()
                print(f'{game_dict[player]["color"]}Turno: {player}. Tus cartas:{Fore.RESET}')
                print('\n'.join(f"{i}: {a.name}({a.number})" for i,a in enumerate(game_dict[player]['mano'])))
                while True:
                    try:
                        index = int(input(game_dict[player]["color"]+'[>]: Indice de carta para tirar: '))
                        tirada = game_dict[player]['mano'].pop(index)
                        #check si puede llevar
                        s = sumer(mesa,15-tirada.number)
                        mesa.append(tirada)
                        for a in s: a.append(tirada)
                        break
                    except Exception:continue
                if s:
                    print(game_dict[player]["color"]+'\n|*| Elije la combinacion para llevar |*|')
                    print('\n'.join(f"{Fore.WHITE}{i}: "+', '.join([f"{a.name}({a.number})" for a in c]) for i,c in enumerate(s)))
                    ultima_llevada = player

                    while True:
                        try:
                            if len(s) ==1:
                                print('Seleccionado automaticamente.')
                                c=0
                            else:
                                c = int(input(game_dict[player]["color"]+'[>]: Indice de la combinacion para llevar: '))
                            if c<len(s):
                                if len(s[c]) == len(mesa):
                                    print(Fore.GREEN+'ESCOBA!')
                                    game_dict[player]['escobas']+=1
                                break
                        except Exception:continue
        
                    for a in s[c]:
                        game_dict[player]['cards'].append(a)
                        mesa.remove(a)
                        
    if mesa:
        print(f"{Fore.RESET}{ultima_llevada} se lleva {len(mesa)} cartas por ser el ultimo en llevar")
        for a in mesa:
            game_dict[ultima_llevada]['cards'].append(a)
    mesa = []

    pt1 = get_cards_amount_winner()
    pt2 = get_oros_amount_winner()
    pt3 = get_sietes_amount_winner()
    print('|******* Puntuacion total: ******|')    
    print('|**** Puntuacion de partida: ****|')  
    for name,stats in game_dict.items():
        print(f'{game_dict[name]["color"]}|  {name}{Fore.RESET}')
        print("\n".join(get_points(name,stats))) 
        print(f'|{"*"*32}|')   
    
    print('|******* Puntuacion total: ******|')
    stats = {a:b['points'] for a,b in game_dict.items()} 
    print('\n'.join(f'{game_dict[a]["color"]}{a}: {b}{Fore.RESET}' for a,b in stats.items()))  
    print(f'|{"*"*32}|') 
    b = get_bigger(stats,'total')
    if len(b) == 1 and stats[b[0]] >= max_points:
        print(f'{game_dict[b[0]]["color"]}{b[0]} gana la partida!!')
        break
    elif len(b) >1: 
        print(f'{Fore.GREEN} Espate! La siguiente ronda es de desempate!')
        jugadores = b

                
                    
print(Fore.RESET)
            


