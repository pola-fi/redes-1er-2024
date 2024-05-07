import socket
from lib.message import Message
from lib.encoder import Encoder

CHUNK_OF_BYTES_RECEIVED = 10000

def send_msg(socket: socket.socket, msg: Message, host, port):
    socket.sendto(Encoder().encode(msg.toJson()), (host,port))

def recive_msg(socket : socket.socket):

    response, server_address = socket.recvfrom(CHUNK_OF_BYTES_RECEIVED)
    received_msg = Encoder().decode(response.decode())

    return received_msg, server_address