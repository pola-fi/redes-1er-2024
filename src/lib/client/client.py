import socket
from lib.message import UploadConnectionMessage
from lib.message import ConnectionDownloadMessage
from lib.message import ResponseUploadMessage
from lib.message import StartDownloadMessage
from lib.message import UploadMessage
from lib.command import Command
from lib.window import Window
from lib.file import File
import base64
import time
import select
import threading
from lib.utilities.socket import send_msg
from lib.utilities.socket import receive_msg
import logging

CHUNK_SIZE = 5000
NUMBER_OF_BYTES_RECEIVED = 10000
TIMEOUT = 1
DIRECTORY_PATH = '/files/client'
SELECTIVE_REPEAT_COUNT = 3

class Client:
    def __init__(self, server_host, server_port, verbose, quiet):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

    ## UPLOAD

    def open_upload_conection(self, file: File):
    
        message = UploadConnectionMessage(file.name, file.get_size())
        logging.info(f"Sending ConectionMessage for file:{file.name} with size:{file.get_size()}")

        send_msg(self.socket, message, self.server_host, self.server_port)
    
        received_msg, server_address = receive_msg(self.socket)

        if received_msg['command'] == Command.RESPONSE_CONNECTION:
            self.server_port = received_msg['server_port']
            logging.info(f"On Server address: {server_address},assigned port: {self.server_port}")

    def upload_file(self, file: File):
        ## Espera para que el server este escuchando
        time.sleep(1)

        offset = 0

        with open(file.absolute_path, 'rb') as open_file:
            while True:
                open_file.seek(offset)
                chunk = open_file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                message = UploadMessage(chunk, offset)
                send_msg(self.socket, message, self.server_host, self.server_port)

                chunk_size = len(chunk)
                offset = self.handle_recive_message(offset, chunk_size)

                logging.debug(f"offset:{offset},chunk size:{chunk_size}")

    def handle_recive_message(self, offset, chunk_size):
        try:
            ready = select.select([self.socket], [], [], TIMEOUT)
            if ready[0]:
                response_message, _ = receive_msg(self.socket)

                if response_message['file_offset'] == offset:
                    offset += chunk_size
            else:
                logging.debug(f"Time out after {TIMEOUT} seconds")
        
            return offset
        
        except socket.timeout:
            logging.debug("Sever Time out")

    ## Selective Upload

    def upload_with_selective_repeat(self, file: File):
        ## Espera para que el server este escuchando
        time.sleep(1)

        self.file = file
        self.window = Window(SELECTIVE_REPEAT_COUNT, CHUNK_SIZE)

        escribir_thread = threading.Thread(target=self.write_chunk_to_socket)
        leer_thread = threading.Thread(target=self.read_ack_of_socket)

        escribir_thread.start()
        leer_thread.start()

        escribir_thread.join()
        leer_thread.join()

    def write_chunk_to_socket(self):
        not_break = True

        with open(self.file.absolute_path, 'rb') as open_file:
            while not_break or (self.window.last_received < self.window.last_sended):
                if self.window.has_space():
                    if self.window.is_empty():
                        offset = self.window.last_received + CHUNK_SIZE
                    else:    
                        offset = self.window.next_sent_element()
                    
                    #print(f"mi offset a enviar es: {offset}")
                    open_file.seek(offset)
                    chunk = open_file.read(CHUNK_SIZE)
                    if not chunk:
                        logging.debug("no hay chunk")
                        # time.sleep(1)
                        not_break = False
                    else: 
                        message = UploadMessage(chunk, offset)

                        self.window.add(offset)
                        logging.debug(f"chunk number sent: {offset / self.window.chunk_size}, offset: {offset}")
                        send_msg(self.socket, message, self.server_host, self.server_port)
                        self.window.last_sended = offset

            logging.debug("termine de mandar escritura")
            logging.debug(f"windows last_received:{self.window.last_received}, windows last_sended:{self.window.last_sended}")


    def read_ack_of_socket(self):

        count_finished_ack = 0
        while count_finished_ack < 3:
            try:
                ready = select.select([self.socket], [], [], TIMEOUT)
                if ready[0]:
                    response_msg, _ = receive_msg(self.socket)
                    response_offset = int(response_msg['file_offset'])

                    logging.debug(f"recived chunk number:{response_offset / CHUNK_SIZE}, offset:{response_offset}")
                    if not self.window.is_empty() and self.window.is_first(response_offset):
                        self.window.remove_first()
                        self.window.last_received = response_offset

                    else: 
                        self.window.remove_all()
                else:
                    if self.window.last_received + self.window.max_size * CHUNK_SIZE > self.file.get_size():
                        count_finished_ack += 1
                    else:
                        logging.debug(f"Time out after {TIMEOUT} seconds")
                    self.window.remove_all()
                        
            except socket.timeout:
                if self.window.last_received + self.window.max_size * CHUNK_SIZE > self.file.get_size():
                    count_finished_ack += 1
                else:
                    logging.debug("Sever Time out")
                self.window.remove_all()
 
    ## Download

    def download_open_conection(self,file: File, windows_size):
        message = ConnectionDownloadMessage(file.name, windows_size)

        send_msg(self.socket, message, self.server_host, self.server_port)
        response_message, server_address = receive_msg(self.socket)
    
        if response_message['command'] == Command.RESPONSE_DOWNLOAD_CONECTION:
            response_port = response_message['server_port']
            file_size = response_message['file_size']
            logging.info(f"Server address: {server_address},responded with port: {response_port}")
            
            message = StartDownloadMessage()
            send_msg(self.socket, message, self.server_host, self.server_port)

            self.socket.close()
            self.server_port = response_port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.server_host, self.server_port))
            logging.info(f"Connection started on host:{self.server_host}, on port:{self.server_port}")

            return file_size

    def download_file(self, file: File, file_size_to_download):

        file.create()
        
        while file.get_size() < file_size_to_download:
            response_message, server_address = receive_msg(self.socket)
            if (response_message['command'] == Command.DOWNLOAD):

                data = base64.b64decode(response_message['file_data'])
                offset = response_message['file_offset']

                logging.debug(f"Recibed data with offset:{offset}")
                file.write(data, offset)
                self.handle_send_ack(offset, server_address)   

    def handle_send_ack(self, offset, client_address):
        message = ResponseUploadMessage(offset)
        send_msg(self.socket, message, client_address[0], client_address[1])