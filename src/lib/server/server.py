import socket
import threading
from lib.server.handle_client import handle_client
from lib.server.upload_client_handler import UploadClientHandler
from lib.command import Command
from lib.encoder import Encoder

RECEIVED_BYTES = 100000

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    def close(self):
        self.socket.close()

    
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

                handler = UploadClientHandler(self.host, new_port, message['file_size'])

                threading.Thread(target=handler.start).start()
                # threading.Thread(target=handle_client, args=(self.host,new_port,)).start()
            

    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, 0))
            return s.getsockname()[1]

    


    