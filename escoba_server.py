from baraja_class import get_baraja,barajar
import tkinter as tk
import random
from threading import Thread
import socket

SEP = '<SEP>'
NL = '<NL>'
jugadores = {}
#jugadores = {nombre:[conn,addr,last_recived]}




def listen_for_messages(conn,addr):
    name = conn.recv(1024)
    if not name:return#DISCONNECTED
    else: name = name.decode()
   
    while jugadores.get(name,None):
        conn.sendall(f'{1}{SEP}{"Nombre ya en uso! escriba otro."}'.encode())
        try:
            name = conn.recv(1024)
        except ConnectionResetError:
            return
        if not name:return#DISCONNECTED
        else: name = name.decode()

    log_widget.insert(tk.END,'\n'+f"Connected to {addr} as {name}")
    jugadores[name] = [conn,addr,'']
    conn.sendall(f'{1}{SEP}{"Conectado como"} {name}.'.encode())

    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            del jugadores[name]
            log_widget.insert(tk.END,'\n'+f'{name} in {addr} is disconnected')
            break #disconnected
        if not data:
            del jugadores[name]
            log_widget.insert(tk.END,'\n'+f'{name} in {addr} is disconnected')
            break #disconnected
        jugadores[name][2] = data.decode()
        log_widget.insert(tk.END,'\n'+f'Recived {jugadores[name][2]} from {addr} as {name}')
        
def listen_for_connections(s):
    while True:
        conn,addr = s.accept()
        thr = Thread(target=listen_for_messages,args=(conn,addr),daemon=True)
        thr.start()
 
def initialize():  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        SERVER_HOST = socket.gethostbyname(socket.gethostname())
        try:
            SERVER_PORT = int(salanumentry.get())+5000
            print(f'port:{SERVER_PORT}')
        except Exception:
            log_widget.insert(tk.END,'\n'+'Invalid room.')
        
        else:

            try:
                s.bind((SERVER_HOST,SERVER_PORT))
                print(f'binded')
            except socket.error as e:
                log_widget.insert(tk.END,'\n'+e)

            #listen for upcoming connections. 
            s.listen()
            print(f'listening')
            log_widget.insert(tk.END,'\n'+f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
            thr = Thread(target=listen_for_connections,args=(s,),daemon=True)
            thr.start()

            #initialize new baraja
            baraja = get_baraja()
            #merge the baraja
            barajar(baraja)
            mesa = []
            ultima_llevada = ''
            
            

            while True:
                try:
                    j_num = int(playersnumentry.get())
                    if j_num < 2: raise Exception
                    break
                except Exception:
                    log_widget.insert(tk.END,'\n'+'Invalid player num. (num > 1)')

            log_widget.insert(tk.END,'\n'+'Waiting for players...')

            while j_num > len(jugadores.keys()):pass#wait for players
            player_names = [a for a in jugadores.keys()]
            last_mov = {name:'' for name in player_names}
            while True:
                try:    
                    max_points = int(pointsentry.get())
                    break
                except Exception:
                    log_widget.insert(tk.END,'\n'+'Invalid points. (points >= 0)')
            
                
            random.shuffle(player_names)
            game_dict = {name:{'mano':[],'escobas':0,'points':0,'cards':[]} for name in player_names}

            def printmesa():
                clear_mesa()
                printallmesa('*'*12+' Mesa '+'*'*12+'\n')
                if mesa:
                    printallmesa('\n'.join([f'{i.name}({i.number})' for i in mesa]))
                else:
                    printallmesa('Mesa vacia')
                printallmesa('\n'+'*'*30+'\n')
                
            def clear_mesa():
                for name in player_names:
                    jugadores[name][0].sendall(f"{3}{SEP}ClearMesa_controlmsg{NL}".encode())

            def printallmesa(msg):
                for name in player_names:
                    jugadores[name][0].sendall(f"{2}{SEP}{msg}{NL}".encode())

            def printall(msg):
                for name in player_names:
                    jugadores[name][0].sendall(f"{1}{SEP}{msg}{NL}".encode())

            def printplayer(msg,conn:socket.socket):
                conn.sendall(f"{1}{SEP}{msg}{NL}".encode())

            def _input(msg,name):
                conn = jugadores[name][0]
                printplayer(msg,conn)
                while not jugadores[name][2]:
                    pass
                last_mov[name] = jugadores[name][2]
                jugadores[name][2] = ''
                return last_mov[name]
                
                
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
                player_names.append(player_names.pop(0))
                for a in game_dict.keys():
                    for b in game_dict[a]['cards']:
                        baraja.append(b)
                    game_dict[a]['cards'] = list()
                barajar(baraja)
                printall('-'*30)
                printall(f'Reparte: {player_names[-1]}. Orden: {" -> ".join(player_names)}')
                printall('-'*30)

                for _ in range(4):
                    mesa.append(baraja.pop(0))
                s = sumer(mesa,15)
                if s:
                    for a in s:
                        if len(a) == 4:
                            printmesa()
                            printall('\n'+f'ESCOBA INICIAL de {player_names[-1]}')
                            for c in a:
                                game_dict[player_names[-1]]['cards'].append(c)
                                mesa.remove(c)
                loops = 12//len(player_names)
                for t in range(loops,0,-1):
                    printall('\n'+'-'*30)
                    printall('Repartiendo...\t'+f'{t} turnos restantes')
                    printall('-'*30)
                    for a in game_dict.keys():
                        for _ in range(3):
                            game_dict[a]['mano'].append(baraja.pop(0))
                        
                    
                    for turno in range(3):
                        for name in player_names:
                            printplayer('\n',jugadores[name][0])
                            printmesa()
                            printall(f'*Turno: {name}'+'\n')
                            printplayer(f'Tus cartas:',jugadores[name][0])
                            printplayer('\n'.join(f"{i}: {a.name}({a.number})" for i,a in enumerate(game_dict[name]['mano'])),jugadores[name][0])
                            while True:
                                try:
                                    index = int(_input('[>]: Indice de carta para tirar: ',name))
                                    print(index,game_dict[name]['mano'],end=':: ')
                                    print(game_dict[name]['mano'][index])
                                    tirada = game_dict[name]['mano'].pop(index)
                                    break
                                except Exception:continue 
                                   
                            #check si puede llevar
                            sm = sumer(mesa,15-tirada.number)
                            mesa.append(tirada)
                            for a in sm: a.append(tirada)
                                    
                                
                            if sm:
                                printplayer('\n|*| Elije la combinacion para llevar |*|',jugadores[name][0])
                                printplayer('\n'.join([f"{i}: "+', '.join([f"{a.name}({a.number})" for a in c]) for i,c in enumerate(s)]),jugadores[name][0])
                                ultima_llevada = name

                                while True:
                                    #try:
                                        if len(sm) ==1:
                                            printplayer('Seleccionado automaticamente.',jugadores[name][0])
                                            c=0
                                        else:
                                            c = int(_input('[>]: Indice de la combinacion para llevar: ',name))
                                        if c<len(sm):
                                            if len(sm[c]) == len(mesa):
                                                game_dict[name]['escobas']+=1
                                            break
                                    #except Exception:continue
                    
                                for a in sm[c]:
                                    game_dict[name]['cards'].append(a)
                                    mesa.remove(a)
                                    
                if mesa:
                    printall(f"{ultima_llevada} se lleva {len(mesa)} cartas por ser el ultimo en llevar")
                    for a in mesa:
                        game_dict[ultima_llevada]['cards'].append(a)
                mesa = []

                pt1 = get_cards_amount_winner()
                pt2 = get_oros_amount_winner()
                pt3 = get_sietes_amount_winner()
                printall('|******* Puntuacion total: ******|')    
                printall('|**** Puntuacion de partida: ****|')  
                for name,stats in game_dict.items():
                    printall(f'|  {name}')
                    printall("\n".join(get_points(name,stats))) 
                    printall(f'|{"*"*32}|')   
                
                printall('|******* Puntuacion total: ******|')
                stats = {a:b['points'] for a,b in game_dict.items()} 
                printall('\n'.join(f'{a}: {b}' for a,b in stats.items()))  
                printall(f'|{"*"*32}|') 
                b = get_bigger(stats,'total')
                if len(b) == 1 and stats[b[0]] >= max_points:
                    printall(f'{b[0]} gana la partida!!')
                    break
                elif len(b) >1: 
                    printall(f'Espate! La siguiente ronda es de desempate!')
                    player_names = b
                    
                    

            
root = tk.Tk()
root.title = 'Hoster'

main_frame = tk.Frame(root); main_frame.pack()
settings_frame = tk.Frame(main_frame);settings_frame.grid(row=0,column=0)

salanumframe = tk.LabelFrame(settings_frame,text='Numero de sala:');salanumframe.grid(row=0,column=0,sticky='EW')
salanumentry = tk.Entry(salanumframe,width=30); salanumentry.pack(fill=tk.BOTH)

playersnumframe = tk.LabelFrame(settings_frame,text='Numero de jugadores:');playersnumframe.grid(row=1,column=0,sticky='EW')
playersnumentry = tk.Entry(playersnumframe); playersnumentry.pack(fill=tk.BOTH)

pointsframe = tk.LabelFrame(settings_frame,text='Puntos para ganar la partida:');pointsframe.grid(row=2,column=0,sticky='EW')
pointsentry = tk.Entry(pointsframe); pointsentry.pack(fill=tk.BOTH)

addr_frame = tk.LabelFrame(settings_frame,text='Public IP addr:'); addr_frame.grid(row=3,column=0,sticky='EW')

ip_addr_1 = socket.gethostbyname(socket.gethostname())
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr_2 = s.getsockname()[0]
s.close()
tk.Label(addr_frame,text=ip_addr_1).pack()
tk.Label(addr_frame,text=ip_addr_2).pack()

log_widget = tk.Text(main_frame);log_widget.grid(row=0,column=1)


tk.Button(root,text='Start Game',command=Thread(target=initialize).start).pack(fill=tk.BOTH)
root.mainloop()


