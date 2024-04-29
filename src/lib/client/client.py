import socket
from lib.message import ConnectionMessage
from lib.message import UploadMessage
from lib.encoder import Encoder
import time

class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def open_conection(self):
        #TODO: agregar size del file
        message = ConnectionMessage("Archivo.txt", 100000)

        self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host,self.server_port))
        response, server_address = self.socket.recvfrom(1024)
        response_data = Encoder().decode(response.decode())


        response_port = response_data['response_port']
        print(f"Server address: {server_address},responded with port: {response_port}")
        self.server_port = response_port

    def upload_file(self, file_name, chunk_size=512):
        ## devolver un ACK para que empieze a escuchar y quitar el wait
        time.sleep(1)
        offset = 0
        with open(file_name, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                message = UploadMessage(chunk.decode(),offset)
                print(f"Sent chunk message:{message.toJson()}, to host:{self.server_host}, on port:{self.server_port}")
                self.socket.sendto(Encoder().encode(message.toJson()), (self.server_host, self.server_port))
                response, _ = self.socket.recvfrom(1024)
                print("Received response:", Encoder().decode(response.decode()))
                offset += len(chunk)