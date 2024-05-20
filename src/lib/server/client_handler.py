import os
import time
import select
import socket
import base64
import logging
import threading

from lib.command import Command
from lib.message import ResponseUploadMessage
from lib.message import DownloadMessage
from lib.window import Window
from lib.utilities.socket import send_msg
from lib.utilities.socket import receive_msg

NUMBER_OF_BYTES_RECEIVED = 10000
DIRECTORY_PATH = '/files/server'
CHUNK_SIZE = 5000
TIMEOUT = 1

class UploadClientHandler:
    def __init__(self, host, port, file_size, file_name, logging):
        self.host = host
        self.port = port
        self.file_size = file_size
        self.file_name = file_name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.logging = logging

    def start(self):
        self.logging.info(f"Server Handler listening on port {self.port}")

        while True:
            message, client_address = receive_msg(self.socket)
            if (message['command'] == Command.UPLOAD):
                self.handle_upload(message, client_address)
    
    def handle_upload(self, message, client_address):
        data = base64.b64decode(message['file_data'])
        offset = message['file_offset']
        self.logging.debug(f"recived msg with chunks: {offset/CHUNK_SIZE}")
        
        self.handle_send_ack(ResponseUploadMessage(offset), client_address)
        
        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)
        self.save_file(path_file, data, offset)
    
    
    def save_file(self, path_file, data, offset):
        if os.path.exists(path_file) and os.path.getsize(path_file) >= offset:
            with open(path_file, 'r+b') as file:
                file.seek(offset)
                file.write(data)
        else:
            with open(path_file, 'ab+') as file:
                file.write(data)

    def handle_send_ack(self, response_message, client_address):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_msg(listener_socket,response_message, client_address[0], client_address[1])
        listener_socket.close()

class DownloadClientHandler:
    def __init__(self, client_host, client_port, file_size, file_name, windows_size):
        self.client_host = client_host
        self.client_port = client_port
        self.file_size = file_size
        self.file_name = file_name
        self.windows_size = windows_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        print(f"Server Handler listening on port {self.client_port}")
        time.sleep(1)

        if self.windows_size == 1:
            self.start_stop_and_wait()
        else: 
            self.start_selective_repeat()

    ## Stop & Wait
        
    def start_stop_and_wait(self):
        offset = 0
        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)

        count_finished_ack = 0

        print(f"path file:{path_file}")
        with open(path_file, 'rb') as file:
            while count_finished_ack < 3:
                file.seek(offset)
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                message = DownloadMessage(chunk ,offset)
                send_msg(self.socket, message, self.client_host, self.client_port)

                offset, count_finished_ack = self.handle_recive_message(offset, chunk, count_finished_ack)

                print(f"offset:{offset},chunk_{len(chunk)}")

    def handle_recive_message(self, offset, chunk, count_finished_ack):
        try:
            ready = select.select([self.socket], [], [], TIMEOUT)
            if ready[0]:
                response_message, _ = receive_msg(self.socket)
                response_offset = response_message['file_offset']
                if response_offset == offset:
                    offset += len(chunk)
            else:
                if offset + CHUNK_SIZE > self.file_size:
                    count_finished_ack += 1 
                else:
                    print("No se recibió respuesta del servidor dentro del tiempo de espera.")
                
        
            return offset, count_finished_ack
        
        except socket.timeout:
            if offset + CHUNK_SIZE > self.file_size:
                count_finished_ack += 1 
            else:
                print("No se recibió respuesta del servidor dentro del tiempo de espera.")
            
            return offset, count_finished_ack
        
    ## Selective Repeat

    def start_selective_repeat(self):

        self.window = Window(self.windows_size, CHUNK_SIZE)

        escribir_thread = threading.Thread(target=self.write_chunk_to_socket)
        leer_thread = threading.Thread(target=self.read_ack_of_socket)

        escribir_thread.start()
        leer_thread.start()

        escribir_thread.join()
        leer_thread.join()
        None
    
    def write_chunk_to_socket(self):

        count_finished_ack = 0

        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)

        with open(path_file, 'rb') as open_file:
            while (count_finished_ack < 3) and (self.window.last_received <= self.window.last_sended):
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
                        count_finished_ack += 1
                    else: 
                        message = DownloadMessage(chunk, offset)

                        self.window.add(offset)
                        logging.debug(f"chunk number sent: {offset / self.window.chunk_size}, offset: {offset}")
                        send_msg(self.socket, message, self.client_host, self.client_port)
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
                    if self.window.last_received + self.window.max_size * CHUNK_SIZE > self.file_size:
                        count_finished_ack += 1
                    else:
                        logging.debug(f"Time out after {TIMEOUT} seconds")
                    
                    self.window.remove_all()
                        
            except socket.timeout:
                if self.window.last_received + self.window.max_size * CHUNK_SIZE > self.file_size:
                    count_finished_ack += 1
                else:
                    logging.debug("Sever Time out")
                self.window.remove_all()
