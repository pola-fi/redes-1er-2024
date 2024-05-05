import socket
from lib.command import Command
from lib.encoder import Encoder
from lib.message import ResponseUploadMessage
from lib.message import DownloadMessage
from lib.encoder import Encoder
import os
import time
import select

BYTES_READ_OF_SOCKET = 100000
DIRECTORY_PATH = '/files/server'
CHUNK_SIZE = 13684
TIMEOUT = 1

class UploadClientHandler:
    def __init__(self, host, port, file_size, file_name):
        self.host = host
        self.port = port
        self.file_size = file_size
        self.file_name = file_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        print(f"Server Handler listening on port {self.port}")

        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        while True:
            data, client_address = self.socket.recvfrom(BYTES_READ_OF_SOCKET)
            #print(f"Received data on port {self.port} from {client_address}: {data}")
            message = Encoder().decode(data.decode())
            # (f"the message:{message}")
            if (message['command'] == Command.UPLOAD):
                prueba_int = self.handle_upload(message, client_address, prueba_int)
    
    def handle_upload(self, message, client_address, prueba_int):
        data = message['file_data']
        offset = message['file_offset']
        response_message = ResponseUploadMessage(offset).toJson()
        
        prueba_int = self.handle_send_ack(response_message, client_address, prueba_int)
        
        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)
        self.save_file(path_file, data, offset)

        prueba_int =+ 1
        return prueba_int
    
    
    def save_file(self, path_file, data, offset):
        # Verificar si el archivo existe y tiene un tamaño mayor o igual al offset
        print(f"directorio actual:{path_file}")
        if os.path.exists(path_file) and os.path.getsize(path_file) >= offset:
            with open(path_file, 'r+b') as file:
                # Mover el puntero de escritura al offset recibido
                file.seek(offset)
                # Escribir los datos en el archivo
                file.write(data.encode())
        else:
            # Si el archivo no existe o el offset es mayor que el tamaño actual del archivo,
            # se crea o se actualiza el archivo desde el principio
            with open(path_file, 'ab+') as file:
                file.write(data.encode())

    #TODO: Vuela, con la perdida de paquetas, queda solo el envio 
    def handle_send_ack(self, response_message, client_address, prueba_int):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #TODO: prueba para simular perdida de paquete, quitar
        if prueba_int % 50 != 0 :
            listener_socket.sendto(Encoder().encode(response_message), client_address)
            listener_socket.close()
        else:
            print("no se envia este ACK")

class DownloadClientHandler:
    def __init__(self, client_host, client_port, file_size, file_name):
        self.client_host = client_host
        self.client_port = client_port
        self.file_size = file_size
        self.file_name = file_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        print(f"Server Handler listening on port {self.client_port}")

        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0
        offset = 0

        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)

        print(f"path file:{path_file}")
        with open(path_file, 'rb') as file:
            while True:
                file.seek(offset)
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                message = DownloadMessage(chunk.decode(),offset)
                #print(f"Sent chunk message:{message.toJson()}, to host:{self.client_host}, on port:{self.client_port}")
                # TODO: Simula la perdida de un paquete cada 100, quitar
                if prueba_int % 5 != 0 :
                    self.socket.sendto(Encoder().encode(message.toJson()), (self.client_host, self.client_port))

                offset = self.handle_recive_message(offset, chunk)

                print(f"offset:{offset},chunk_{len(chunk)}")
                    
                prueba_int += 1

    def handle_recive_message(self, offset, chunk):
        try:
            ready = select.select([self.socket], [], [], TIMEOUT)
            if ready[0]:
                response, _ = self.socket.recvfrom(1024)
                response_decoded = Encoder().decode(response.decode())
                response_offset = response_decoded['file_offset']
                if response_offset == offset:
                    offset += len(chunk)
            else:
                # El temporizador ha expirado, no se recibió ninguna respuesta
                print("No se recibió respuesta del servidor dentro del tiempo de espera.")
        
            return offset
        
        except socket.timeout:
            # El temporizador ha expirado, no se recibió ninguna respuesta
            print("No se recibió respuesta del servidor dentro del tiempo de espera.")
            return offset

        # while True:
        #     # Parsear el archivo y enviar
        #     #self.socket.sendto(Encoder().encode(response_message), client_address)


        #     data, client_address = self.socket.recvfrom(BYTES_READ_OF_SOCKET)
        #     #print(f"Received data on port {self.port} from {client_address}: {data}")
        #     message = Encoder().decode(data.decode())
        #     # (f"the message:{message}")
        #     if (message['command'] == Command.UPLOAD):
        #         prueba_int = self.handle_upload(message, client_address, prueba_int)