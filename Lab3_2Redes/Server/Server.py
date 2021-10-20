import socket
import threading
from os import path
import time
import struct as st

PORT = 9001
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FILES_DIR = 'archivos'
LOGS_DIR = 'logs'

all_conns = []
abs_path = path.dirname(path.abspath(__file__))
files_path = path.join(abs_path,FILES_DIR)
logs_path = path.join(abs_path,LOGS_DIR)
global server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(ADDR)


# Elige que archivo se va a enviar y a cuantos clientes se va a esperar
def iniciar_server():
    try:
        global file_path
        global file_name
        global file_size
        global hash_local
        global num_usuarios
        
        del all_conns[:]
        global num_usuarios
        num_usuarios = int(input('Numero de usuarios a enviar>> '))
        
        files = ['100.txt', '250.txt']
        file_name = files[int(input('Ingrese el archivo que desea usar (0 para 100Mb) (1 para 250Mb)>> '))]
        file_path = path.join(files_path,file_name)
        file_size = path.getsize(file_path)
    
    except Exception as e :
        print('Ocurrio un error con las opciones elegidas',str(e))
        iniciar_server()

# Atiende las diferentes peticiones
def correr_server():
    serverNum = 0
    print(f"Server escuchando en {SERVER}")
    # Acepta todas las conexiones e inicia un thread para enviar cuando todos esten listos
    while True:
        try:
            data1, addr = server.recvfrom(4096)
            server.setblocking(1)
            client = ClientThread(addr,serverNum)
            serverNum = serverNum + 1
            
            global all_conns
            all_conns.append(client)
            client.start()
            print ('Nueva conexion de ', addr)
            if len(all_conns) == num_usuarios:
                print('Los usuarios estan todos conectados!')
                
                flag_enviado = False
                while not flag_enviado:
                    all_ready = True
                    for conns in all_conns:
                        all_ready = conns.ready and all_ready                        
                    flag_enviado = all_ready
                for conns in all_conns:
                    conns.send = flag_enviado
                del all_conns[:]

        except Exception as e:
            print ('Fallo al conseguir las conexiones', str(e))
    server.close()

# Thread que da manejo a cada cliente
class ClientThread(threading.Thread):
    
    def __init__(self, addr,serverNum):
        threading.Thread.__init__(self)
        self.addr = addr
        self.ready = False
        self.terminar = True
        self.send = False
        self.serverNum =  serverNum
    
    def run(self):
        #Se crea el log para escribir los resultados
        name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+'-log'+str(self.serverNum)+'.txt'
        log = open(path.join(logs_path, name),'w')
        
        self.ready = True
        console_msg = 'La conexion {} esta lista \n'.format(self.addr)
        print (console_msg)
        log.write('Se le envia al cliente {} \n'.format(self.addr))

        
        #Espera a poder enviar
        while self.terminar and not self.send:
            continue
        if self.terminar and self.send:
            server.sendto(file_name.encode(FORMAT), self.addr)
            log.write('Se envia el archivo {} \n'.format(file_name))
            
            # Se abre el archivo
            f = open(file_path, 'rb')
            
            #Se encapsula el tamano y se envia 
            file_size_encoded = st.pack('I', file_size)
            server.sendto(file_size_encoded, self.addr)
            log.write('El archivo pesa {} \n'.format(file_size))
            line = f.read(1024)
            start_time = time.time()
            
            # Se itera sobre el archivo para enviarse por paquetes
            while line:
                server.sendto(line, self.addr)
                line = f.read(1024)
            
            
            # Se lee si el cliente confirma que fue correcto o no
            data2 , addr = server.recvfrom(255)
            data2 = data2.decode(FORMAT)
            if data2 == "ok":
                log.write('El archivo se envio satisfactoriamente \n')
            else:
                log.write('El archivo no se envio satisfactoriamente\n')
            
            # Se toma y envia el tiempo al cliente
            data3 , addr = server.recvfrom(8).decode(FORMAT)
            stop_time = float(st.unpack('d',data3)[0])
            total_time = abs(start_time - stop_time)
            while data2 and data3:
                continue
            server.sendto(st.pack('d',total_time), self.addr)
            
            
            # Se registra el tiempo y se cierra
            log.write('Tiempo de transmicion fue: {} s \n'.format(round(total_time,3) ))
            log.close()
            self.conn.close()
        else:
            log.close()
            self.conn.close()
                
                
iniciar_server()
correr_server()