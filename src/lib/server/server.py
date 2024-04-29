import socket
import threading
import json
from lib.command import Command
from lib.encoder import Encoder

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
        while True:
            data, client_address = listener.recvfrom(100000)
            print(f"Received data on port {port} from {client_address}: {data}")
            message = Encoder().decode(data.decode())
            if (message['command'] == Command.UPLOAD):
                self.handle_upload(message, client_address)
    
    def handle_upload(self, message, client_address):
        response_message = {'response': 'Upload received successfully'}
        response_data = json.dumps(response_message).encode()
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_socket.sendto(response_data, client_address)
        listener_socket.close()

    