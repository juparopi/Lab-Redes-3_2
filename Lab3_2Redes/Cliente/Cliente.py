import socket
import time
import hashlib
import struct as st
from os import path
import threading

numClientes = int(input('Ingrese el numero de clientes que desea crear>> '))


def clientFunction(name):
    
    UDPPORT = name +9500
    PORT = 9011
    FORMAT = 'utf-8'
    SERVER = "192.168.231.128"
    #SERVER = "127.0.0.1"
    ADDR = (SERVER, PORT)
    FILES_DIR = 'archivos'
    LOGS_DIR = 'logs'
    
    
    abs_path = path.dirname(path.abspath(__file__))
    files_path = path.join(abs_path,FILES_DIR)
    logs_path = path.join(abs_path,LOGS_DIR)
    
    def obtener_hash(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        f.close()
        return hash_md5.digest()
    
    # Se crea el socket
    s = socket.socket()
    s.connect(ADDR)
    
    #Se crea el socket udp
    sUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Se crea el log
    file_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+'-log'+str(name)+'.txt'
    log = open(path.join(logs_path, file_name),'w')
    
    # Recibe si el server esta listo
    console_msg = str(s.recv(255).decode(FORMAT))

    
    # Saluda al cliente
    s.send("Ready".encode(FORMAT))
    
    # Se registra el nombre del archivo
    file_name = str(s.recv(255).decode(FORMAT))
    log.write('Se recibe el archivo {} \n'.format(file_name))
    
    
    file_name = "Cliente"+str(name)+"-Prueba-"+str(numClientes)+".txt"
    file_path = path.join(files_path,file_name)
    
    #Inicia la conexion udp
    sUDP.sendto(b'Hello', (SERVER, UDPPORT))
    
    # Se extrae el archivo y se determina su peso
    with open(file_path, 'wb') as f:
        # Se recibe el tamaño del archivo
        file_size = int(st.unpack('I',s.recv(4))[0])
        log.write('El archivo pesa {} bytes\n'.format(file_size))
        # Se guarda el archivo en el cliente    
        flag = True;
        while flag:
            flag_tcp = str(s.recv(255).decode(FORMAT))
            data , addrudp = sUDP.recvfrom(1024)
            f.write(data)
            if flag_tcp.endswith('o'):
                flag = False
                break
        f.close()
    sUDP.close()
    s.send('Archivo recibido'.encode(FORMAT))
    # Se recibe el hash del server
    checksum = s.recv(64)
    checksum_local = obtener_hash(file_path)
    
    # Se determina si el archivo llego correctamente o no
    if checksum == checksum_local:
        s.send("ok".encode(FORMAT))
        console_msg = 'El archivo de '+str(file_size)+" bytes se recibio de forma exitosa"
        log.write(console_msg+'\n')
        print(console_msg)
    else:
        s.send("not ok".encode(FORMAT))
        console_msg = 'El archivo '+str(name)+' no se recibio bien'
        log.write(console_msg+'\n')
        print(console_msg)
    
    # Se envia el tiempo de terminacion
    s.send(st.pack('d',time.time()))
    
    # Se recibe el tiempo total
    total_time = float(st.unpack('d',s.recv(8))[0])
    log.write('Tiempo de transmicion fue: {} s \n'.format(round(total_time,3) ))
    log.write(console_msg+'\n')
    
    # Se cierra todo
    s.close()
    console_msg = 'Se cierra la conexion'
    print(console_msg , name)
    log.close()
    
    
    
clientes = []
for i in range(numClientes):
    t = threading.Thread(name='Cliente'+str(i), target=clientFunction, args=(i,))
    clientes.append(t)
    t.start()