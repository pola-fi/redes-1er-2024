import socket
import threading
from lib.server.upload_client_handler import UploadClientHandler
from lib.server.upload_client_handler import DownloadClientHandler
from lib.command import Command
from lib.encoder import Encoder
from lib.message import ResponseConnectionDownloadMessage
import os
import time
import logging

RECEIVED_BYTES = 100000
DIRECTORY_PATH = '/files/server'

class Server:
    def __init__(self, host, port, dir_path, verbose, quiet):
        self.host = host
        self.port = port
        self.dir_path = dir_path
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if verbose == False and quiet == False:
            level='INFO'
            logging.basicConfig(level=level)
        if verbose:
            level='DEBUG'
            logging.basicConfig(level=level)
        if quiet:
            level='ERROR'
            logging.basicConfig(level=level)      
            
    def close(self):
        self.socket.close()

    
    def listen(self):
        logging.info(f"Server listening on {self.host}:{self.port}")
        while True:
            data, client_address = self.socket.recvfrom(RECEIVED_BYTES)
            message = Encoder().decode(data.decode())
            logging.debug(f"Received message from {client_address}: {message}")
            
            if message['command'] == Command.CONNECTION:
                new_port = self.find_free_port()
                logging.info(f"Assigned port {new_port} to client {client_address}")
                response_message = {'response_port': new_port}
                self.socket.sendto(Encoder().encode(response_message), client_address)

                handler = UploadClientHandler(self.host, new_port, message['file_size'], message['file_name'],logging)

                threading.Thread(target=handler.start).start()
                # threading.Thread(target=handle_client, args=(self.host,new_port,)).start()

            elif message['command'] == Command.DOWNLOAD_CONECTION:
                
                file_name = message['file_name']
                if self.exist_file(file_name):
                    new_port = self.find_free_port()
                    response_message = ResponseConnectionDownloadMessage(new_port, self.get_size(file_name))
                    logging.info(f"Assigned port {new_port} to client {client_address}")
                    self.socket.sendto(Encoder().encode(response_message.toJson()), client_address)

                    data, client_address = self.socket.recvfrom(RECEIVED_BYTES)
                    message_start_ack = Encoder().decode(data.decode())
                    logging.debug(f"mesnsaje:{message}")

                    if message_start_ack['command'] == Command.DOWNLOAD_START:
                        logging.info("Client Started listening for download")
                        handler = DownloadClientHandler(self.host, new_port, self.get_size(file_name), file_name)
                        threading.Thread(target=handler.start).start()
                    
           
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, 0))
            return s.getsockname()[1]
        
    def exist_file(self, file_name):
        path_file = os.path.join(os.getcwd(),self.dir_path.lstrip('/'), file_name)
        if os.path.exists(path_file):
            return True
        else: 
            return False
        
    def get_size(self, file_name):
        path_file = os.path.join(os.getcwd(),self.dir_path.lstrip('/'), file_name)
        return os.path.getsize(path_file)

    


    