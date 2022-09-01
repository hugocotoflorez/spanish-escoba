
import socket
from threading import Thread
from tkinter.ttk import Labelframe
import tkinter as tk
import re

SEP = '<SEP>'
NL = '<NL>'
IP_REGEX = re.compile(r"([1-2]?[0-9]?[0-9])\.([1-2]?[0-9]?[0-9])\.([1-2]?[0-9]?[0-9])\.([1-2]?[0-9]?[0-9])")

root = tk.Tk()
root.geometry('300x400')
root.title = 'Escoba online'
join_frame = tk.Frame(root); join_frame.pack(fill=tk.BOTH)
join_sala_frame = tk.LabelFrame(join_frame,text='Numero de sala:');join_sala_frame.pack(fill=tk.BOTH)
sala_entry = tk.Entry(join_sala_frame);sala_entry.pack(fill=tk.BOTH)
join_addr_frame = tk.LabelFrame(join_frame,text='IP del server:');join_addr_frame.pack(fill=tk.BOTH)
addr_entry = tk.Entry(join_addr_frame);addr_entry.pack(fill=tk.BOTH)
addr_entry.insert(tk.END,'LOCALHOST')

def _validate():
    if sala_entry.get().isnumeric():
        if IP_REGEX.search(addr_entry.get()) or addr_entry.get() == 'LOCALHOST':
            join_frame.forget() 
            _next()
        else:
            addr_entry.insert(tk.END,'Invalid addr')
    else:
        sala_entry.insert(tk.END,'Invalid room')
        
tk.Button(join_frame,text='Join',command=Thread(target=_validate).start).pack(fill=tk.BOTH)

def _next():
    root.geometry('1050x450')
    text_frame = tk.Frame(root);text_frame.pack()
    mano_lf = Labelframe(text_frame,text='Mano');mano_lf.grid(row=0,column=0) 
    text_widget = tk.Text(mano_lf);text_widget.pack(side="left", fill="both", expand=True)
    vsb = tk.Scrollbar(mano_lf, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    mesa_lf = Labelframe(text_frame,text='Mesa');mesa_lf.grid(row=0,column=1)
    mesa_widget = tk.Text(mesa_lf);mesa_widget.pack()
    main_frame = tk.Frame(root);main_frame.pack(fill=tk.BOTH)
    text_widget.insert(tk.END,'Send your name to join the game')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        input_addr = addr_entry.get()
        SERVER_HOST = socket.gethostbyname(socket.gethostname()) if input_addr == 'LOCALHOST' else input_addr
        SERVER_PORT = int(sala_entry.get())+5000

        try:
            s.connect((SERVER_HOST,SERVER_PORT))
        
        except Exception as e:
            print('Impossible to connect')


        tk.Label(root,text=f"Connected to {SERVER_HOST}:{SERVER_PORT}").pack()
        
        def print_recv():
            while True:
                data = s.recv(1024)
                if not data: break 
                data = data.decode()
                for line in data.rstrip(NL).split(NL):
                    splited_line = line.split(SEP)
                    print(splited_line,line)
                    code,msg,*c = splited_line
                    if c:
                        print('Exceded:',c)

                    if code == '1':
                        text_widget.insert(tk.END,"\n"+msg)
                        text_widget.see("end")
                    elif code == '2':
                        mesa_widget.insert(tk.END,msg)
                        text_widget.see("end")
                    elif code == '3':
                        mesa_widget.delete('1.0',tk.END)
                    else:
                        print('invalid code:',code)
            print('Disconnected')
            
        def send():
            to_send = send_widget.get()
            send_widget.delete(0,tk.END)
            s.send(to_send.encode()) 
        
        send_widget = tk.Entry(main_frame,width=60);send_widget.grid(row=0,column=0)
        send_button = tk.Button(main_frame,text='Send',command=send,width=20);send_button.grid(row=0,column=1)
        
        
        print_recv()

    
  
target=root.mainloop()