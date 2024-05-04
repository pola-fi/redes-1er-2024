import socket
import threading
import json
from lib.command import Command
from lib.encoder import Encoder
from lib.message import ResponseUploadMessage
from lib.encoder import Encoder
import os

RECEIVED_BYTES = 100000

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    
    def listen(self):
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            data, client_address = self.socket.recvfrom(1024)
            message = Encoder().decode(data.decode())
            print(f"Received message from {client_address}: {message}")

            if message['command'] == Command.CONNECTION:
                new_port = self.find_free_port()
                print(f"Assigned port {new_port} to client {client_address}")
                response_message = {'response_port': new_port}
                self.socket.sendto(Encoder().encode(response_message), client_address)
                threading.Thread(target=self.handle_client, args=(new_port,)).start()
            

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, 0))
            return s.getsockname()[1]

    def handle_client(self, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener.bind((self.host, port))
        print(f"Server listening on port {port}")

        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        while True:
            data, client_address = listener.recvfrom(100000)
            print(f"Received data on port {port} from {client_address}: {data}")
            message = Encoder().decode(data.decode())
            print(f"the message:{message}")
            if (message['command'] == Command.UPLOAD):
                prueba_int = self.handle_upload(message, client_address, prueba_int)
    
    def handle_upload(self, message, client_address, prueba_int):
        data = message['file_data']
        offset = message['file_offset']
        response_message = ResponseUploadMessage(offset).toJson()
        
        prueba_int = self.handle_send_ack(response_message, client_address, prueba_int)
        
        self.save_file("llegada.txt", data, offset)

        prueba_int =+ 1
        return prueba_int

    def save_file(self, file_name, data, offset):
    # Verificar si el archivo existe y tiene un tamaño mayor o igual al offset
        if os.path.exists(file_name) and os.path.getsize(file_name) >= offset:
            with open(file_name, 'r+b') as file:
                # Mover el puntero de escritura al offset recibido
                file.seek(offset)
                # Escribir los datos en el archivo
                file.write(data.encode())
        else:
            # Si el archivo no existe o el offset es mayor que el tamaño actual del archivo,
            # se crea o se actualiza el archivo desde el principio
            with open(file_name, 'ab') as file:
                file.write(data.encode())

    def handle_send_ack(self, response_message, client_address, prueba_int):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if prueba_int % 50 != 0 :
            listener_socket.sendto(Encoder().encode(response_message), client_address)
            listener_socket.close()
        else:
            print("no se envia este ACK")


    