import os
import time
import select
import socket
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

        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0

        while True:
            message, client_address = receive_msg(self.socket)
            if (message['command'] == Command.UPLOAD):
                prueba_int = self.handle_upload(message, client_address, prueba_int)
    
    def handle_upload(self, message, client_address, prueba_int):
        data = message['file_data']
        offset = message['file_offset']
        self.logging.debug(f"recived msg with chunks: {offset/CHUNK_SIZE}")
        #response_message = .toJson()
        
        prueba_int = self.handle_send_ack(ResponseUploadMessage(offset), client_address, prueba_int)
        
        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)
        self.save_file(path_file, data, offset)

        prueba_int =+ 1
        return prueba_int
    
    
    def save_file(self, path_file, data, offset):
        # Verificar si el archivo existe y tiene un tamaño mayor o igual al offset
        # self.logging.debug(f"directorio actual:{path_file}")
        if os.path.exists(path_file) and os.path.getsize(path_file) >= offset:
            with open(path_file, 'r+b') as file:
                # Mover el puntero de escritura al offset recibido
                file.seek(offset)
                # Escribir los datos en el archivo
                file.write(data.encode())
        else:
            # Si el archivo no existe o el offset es mayor que el tamaño actual del archivo,
            # se crea o se actualiza el archivo desde el principio
            with open(path_file, 'ab+') as file:
                file.write(data.encode())

    #TODO: Vuela, con la perdida de paquetas, queda solo el envio 
    def handle_send_ack(self, response_message, client_address, prueba_int):
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #TODO: prueba para simular perdida de paquete, quitar
        if prueba_int % 3 != 0 :
            send_msg(listener_socket,response_message, client_address[0], client_address[1])
            listener_socket.close()
        else:
           print("no se envia este ACK")

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

        # TODO: Simula la perdida de un paquete cada 100, quitar
        prueba_int = 0
        offset = 0

        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)

        print(f"path file:{path_file}")
        with open(path_file, 'rb') as file:
            while True:
                file.seek(offset)
                chunk = file.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                message = DownloadMessage(chunk.decode(),offset)
                #print(f"Sent chunk message:{message.toJson()}, to host:{self.client_host}, on port:{self.client_port}")
                # TODO: Simula la perdida de un paquete cada 100, quitar
                if prueba_int % 5 != 0 :
                    send_msg(self.socket, message, self.client_host, self.client_port)

                offset = self.handle_recive_message(offset, chunk)

                print(f"offset:{offset},chunk_{len(chunk)}")
                    
                prueba_int += 1

    def handle_recive_message(self, offset, chunk):
        try:
            ready = select.select([self.socket], [], [], TIMEOUT)
            if ready[0]:
                response_message, _ = receive_msg(self.socket)
                response_offset = response_message['file_offset']
                if response_offset == offset:
                    offset += len(chunk)
            else:
                # El temporizador ha expirado, no se recibió ninguna respuesta
                print("No se recibió respuesta del servidor dentro del tiempo de espera.")
        
            return offset
        
        except socket.timeout:
            # El temporizador ha expirado, no se recibió ninguna respuesta
            print("No se recibió respuesta del servidor dentro del tiempo de espera.")
            return offset
        
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

        number_of_packet = 1
        not_break = True

        path_file = os.path.join(os.getcwd(),DIRECTORY_PATH.lstrip('/'), self.file_name)

        with open(path_file, 'rb') as open_file:
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
                        message = DownloadMessage(chunk.decode(), offset)

                        #print(f"Sent chunk message:{message.toJson()}, to host:{self.server_host}, on port:{self.server_port}")
                        # TODO: Simula la perdida de un paquete cada 100, quitar
                        
                        if number_of_packet % 3 != 0 :

                            self.window.add(offset)
                            logging.debug(f"chunk number sent: {offset / self.window.chunk_size}, offset: {offset}")
                            send_msg(self.socket, message, self.client_host, self.client_port)
                            self.window.last_sended = offset                    

                        number_of_packet += 1

                    
                # else: 
                #     print(f"windows dont have space")
                #     time.sleep(1)
            logging.debug("termine de mandar escritura")
            logging.debug(f"windows last_received:{self.window.last_received}, windows last_sended:{self.window.last_sended}")


    def read_ack_of_socket(self):
        while True:
                
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
                    # El temporizador ha expirado, no se recibió ninguna respuesta
                    logging.debug(f"Time out after {TIMEOUT} seconds")
                    self.window.remove_all()
                        
            except socket.timeout:
                # El temporizador ha expirado, no se recibió ninguna respuesta
                logging.debug("Sever Time out")
                self.window.remove_all()
