import socket
from lib.message import ConnectionMessage
from lib.message import UploadMessage
from lib.encoder import Encoder
import time
import os
import select

CHUNK_SENT_BYTES = 32768 
TIMEOUT = 1

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        self.socket.close()

        
    def obtener_tamano_archivo(self, ruta):
        # Verificar si el archivo existe
        if os.path.exists(ruta):
            # Obtener el tamaño en bytes del archivo
            tamano = os.path.getsize(ruta)
            return tamano

    def open_conection(self, file_path,file_name):
        #TODO: agregar size del file
        file_size = self.obtener_tamano_archivo(os.path.join(file_path, file_name))
        print(f"file size:{file_size}")
        message = ConnectionMessage(file_name, file_size)

        self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host,self.server_port))
        response, server_address = self.socket.recvfrom(1024)
        response_data = Encoder().decode(response.decode())


        response_port = response_data['response_port']
        print(f"Server address: {server_address},responded with port: {response_port}")
        self.server_port = response_port

    def upload_file(self, file_path, file_name, chunk_size=CHUNK_SENT_BYTES):
        ## devolver un ACK para que empieze a escuchar y quitar el wait
        time.sleep(1)
        
        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        offset = 0

        path_file = os.path.join(file_path, file_name)

        print()

        with open(path_file, 'rb') as file:
            while True:
                file.seek(offset)
                chunk = file.read(chunk_size)
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
