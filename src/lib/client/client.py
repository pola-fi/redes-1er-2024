import socket
from lib.message import ConnectionMessage
from lib.message import ConnectionDownloadMessage
from lib.message import ResponseUploadMessage
from lib.message import StartDownloadMessage
from lib.message import UploadMessage
from lib.encoder import Encoder
from lib.command import Command
from lib.file import File
import time
import os
import select

CHUNK_OF_BYTES_READ = 32768 
CHUNK_OF_BYTES_SENT = 32768 
TIMEOUT = 1
DIRECTORY_PATH = '/files/client'

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        self.socket.close()

    def open_conection(self, file: File):
    
        message = ConnectionMessage(file.name, file.size)
        print(f"Sending ConectionMessage for file:{file.name} with size:{file.size}")

        self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host,self.server_port))

        response, server_address = self.socket.recvfrom(1024)
        response_data = Encoder().decode(response.decode())

        self.server_port = response_data['response_port']
        print(f"Server address: {server_address},assigned port: {self.server_port}")
 

    def upload_with_selective_repeat(self, file: File):
        

    def upload_file(self, file: File):
        ## Espera para que el server este escuchando
        time.sleep(1)
        
        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        offset = 0

        with open(file.absolute_path, 'rb') as open_file:
            while True:
                open_file.seek(offset)
                chunk = open_file.read(CHUNK_OF_BYTES_READ)
                if not chunk:
                    break
                
                message = UploadMessage(chunk.decode(),offset)
                # print(f"Sent chunk message:{message.toJson()}, to host:{self.server_host}, on port:{self.server_port}")
                # TODO: Simula la perdida de un paquete cada 100, quitar
                if prueba_int % 100 != 0 :
                    self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host, self.server_port))

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

    def download_open_conection(self,file_name):
        message = ConnectionDownloadMessage(file_name)

        self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host,self.server_port))
        response, server_address = self.socket.recvfrom(1024)
        response_message = Encoder().decode(response.decode())

    
        if response_message['command'] == Command.RESPONSE_DOWNLOAD_CONECTION:
            response_port = response_message['server_port']
            print(f"Server address: {server_address},responded with port: {response_port}")
            
            message = StartDownloadMessage()
            self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host,self.server_port))
            self.socket.close()
            self.server_port = response_port
        
    
    def download_file(self, file_path, file_name):
        ## devolver un ACK para que empieze a escuchar y quitar el wait
        
        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        path_file = os.path.join(os.getcwd(), file_path.lstrip('/'), file_name)

        print(f"path:{path_file}")

        print(f"Connection started on host:{self.server_host}, on port:{self.server_port}-")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.server_host, self.server_port))

        while True:
            
            data, server_address = self.socket.recvfrom(CHUNK_SENT_BYTES)
            # print(f"Received data on port {self.server_port} from {server_address}")
            message = Encoder().decode(data.decode())
            # print("recibi un msg y decodifique")
            # (f"the message:{message}")
            if (message['command'] == Command.DOWNLOAD):
                # print("es un DOWNLOAD msg")
                prueba_int = self.handle_upload(message, server_address, path_file, prueba_int)


    def handle_upload(self, message, client_address, file_path, prueba_int):
        data = message['file_data']
        offset = message['file_offset']
        print(f"Recibed data with offset:{offset}")
        response_message = ResponseUploadMessage(offset).toJson()
                
        self.save_file(file_path, data, offset)
        prueba_int = self.handle_send_ack(response_message, client_address, prueba_int)

        prueba_int =+ 1
        return prueba_int
    
    
    def save_file(self, path_file, data, offset):
        # Verificar si el archivo existe y tiene un tamaño mayor o igual al offset
        if os.path.exists(path_file) and os.path.getsize(path_file) >= offset:
            with open(path_file, 'r+b') as file:
                # Mover el puntero de escritura al offset recibido
                file.seek(offset)
                # Escribir los datos en el archivo
                file.write(data.encode())
        else:
            # Si el archivo no existe o el offset es mayor que el tamaño actual del archivo,
            # se crea o se actualiza el archivo desde el principio
            with open(path_file, 'ab') as file:
                file.write(data.encode())

    #TODO: Vuela, con la perdida de paquetas, queda solo el envio 
    def handle_send_ack(self, response_message, client_address, prueba_int):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #TODO: prueba para simular perdida de paquete, quitar
        if prueba_int % 3 != 0 :
            listener_socket.sendto(Encoder().encode(response_message), client_address)
        # listener_socket.close()
        else:
            print("no se envia este ACK")
