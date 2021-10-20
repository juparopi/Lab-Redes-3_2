import socket
import time
import struct as st
from os import path
import threading

numClientes = int(input('Ingrese el numero de clientes que desea crear>> '))

def clientFunction(name):
    PORT = 9006
    FORMAT = 'utf-8'
    SERVER = "127.0.0.1"
    ADDR = (SERVER, PORT)
    FILES_DIR = 'archivos'
    LOGS_DIR = 'logs'
    
    
    abs_path = path.dirname(path.abspath(__file__))
    files_path = path.join(abs_path,FILES_DIR)
    logs_path = path.join(abs_path,LOGS_DIR)

    # Se crea el socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Se crea el log
    file_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+'-log'+str(name)+'.txt'
    log = open(path.join(logs_path, file_name),'w')
    
    # Saluda al cliente
    s.sendto("Ready".encode(FORMAT),ADDR)
    
    # Se registra el nombre del archivo
    data1 , addr = s.recvfrom(255)
    file_name = str(data1.decode(FORMAT))
    log.write('Se recibe el archivo {} \n'.format(file_name))
    
    
    file_name = "Cliente"+str(name)+"-Prueba-"+str(numClientes)+".txt"
    file_path = path.join(files_path,file_name)
    
    # Se extrae el archivo y se determina su peso
    with open(file_path, 'wb') as f:
        # Se recibe el tamaño del archivo
        data2, addr = s.recv(4)
        file_size = int(st.unpack('I',data2)[0])
        log.write('El archivo pesa {} bytes\n'.format(file_size))
    
        # Se guarda el archivo en el cliente    
        total_file_size = 0
        while total_file_size < file_size:
            data3, addr = s.recvfrom(10*1024)
            total_file_size+=len(data3)
            f.write(data3)
        f.close()
    file_size_local = path.getsize(file_path) 
    
    # Se determina si el archivo llego correctamente o no
    if file_size_local == file_size:
        s.sendto("ok".encode(FORMAT), ADDR)
        console_msg = 'El archivo de '+str(file_size)+" bytes se recibio de forma exitosa"
        log.write(console_msg+'\n')
    else:
        s.sendto("not ok".encode(FORMAT),ADDR)
        console_msg = 'El archivo no se recibio bien'
        log.write(console_msg+'\n')
        
    
    # Se envia el tiempo de terminacion
    s.sendto(st.pack('d',time.time()), ADDR)
    
    
    # Se recibe el tiempo total
    data4 , addr = s.recvfrom(8)
    total_time = float(st.unpack('d',data4)[0])
    log.write('Tiempo de transmicion fue: {} s \n'.format(round(total_time,3) ))
    log.write(console_msg+'\n')
    
    # Se cierra todo
    s.close()
    console_msg = 'Se cierra la conexion'
    log.close()
    
    
    
clientes = []
for i in range(numClientes):
    t = threading.Thread(name='Cliente'+str(i), target=clientFunction, args=(i,))
    clientes.append(t)
    t.start()