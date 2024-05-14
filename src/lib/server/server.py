import threading
import logging
import socket
import os

from lib.server.client_handler import UploadClientHandler
from lib.server.client_handler import DownloadClientHandler
from lib.command import Command
from lib.message import ResponseConnectionDownloadMessage
from lib.message import ResponseUploadConectionMessage
from lib.utilities.socket import send_msg
from lib.utilities.socket import receive_msg


RECEIVED_BYTES = 100000
DIRECTORY_PATH = '/files/server'
SELECTIVE_REPEAT_COUNT = 1

class Server:
    def __init__(self, host, port, dir_path, verbose, quiet):
        self.host = host
        self.port = port
        self.dir_path = dir_path
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

        if verbose == False and quiet == False:
            level='INFO'
            logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s',level=level)
        if verbose:
            level='DEBUG'
            logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s',level=level)
        if quiet:
            level='ERROR'
            logging.basicConfig(format='%(levelname)s : %(asctime)s : %(message)s',level=level)      
            
    def close(self):
        self.socket.close()

    
    def listen(self):
        logging.info(f"Server listening on {self.host}:{self.port}")
        while True:
            try:
                message, client_address = receive_msg(self.socket)
            except KeyboardInterrupt:
                break
            logging.debug(f"Received message from {client_address}: {message}")
            
            if message['command'] == Command.UPLOAD_CONNECTION:
                new_port = self.find_free_port()
                logging.info(f"Assigned port {new_port} to client {client_address}")
                response_message = ResponseUploadConectionMessage(new_port)
                send_msg(self.socket, response_message, client_address[0], client_address[1])

                handler = UploadClientHandler(self.host, new_port, message['file_size'], message['file_name'],logging)

                threading.Thread(target=handler.start).start()

            elif message['command'] == Command.DOWNLOAD_CONECTION:
                
                file_name = message['file_name']
                windows_size = message['windows_size']
                if self.exist_file(file_name):
                    new_port = self.find_free_port()
                    response_message = ResponseConnectionDownloadMessage(new_port, self.get_size(file_name))
                    logging.info(f"Assigned port {new_port} to client {client_address}")
                    send_msg(self.socket, response_message, client_address[0], client_address[1])

                    message_decoded, client_address = receive_msg(self.socket)
                    logging.debug(f"mensaje:{message_decoded}")

                    if message_decoded['command'] == Command.DOWNLOAD_START:
                        logging.info("Client Started listening for download")
                        handler = DownloadClientHandler(self.host, new_port, self.get_size(file_name), file_name, windows_size)
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

    


    