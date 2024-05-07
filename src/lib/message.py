from lib.command import Command
from abc import ABC, abstractmethod

class Message(ABC):
    def __init__(self, command):
        self.command = command

    @abstractmethod
    def toJson(self):
        pass

class UploadConnectionMessage(Message):
    def __init__(self, file_name ,file_size):
        super().__init__(Command.UPLOAD_CONNECTION)
        self.file_size = file_size
        self.file_name = file_name
    
    def toJson(self):
        return {
            'command': self.command,
            'file_size': self.file_size,
            'file_name': self.file_name
        }
    
class ResponseUploadConectionMessage(Message):
    def __init__(self, port):
        super().__init__(Command.RESPONSE_CONNECTION)
        self.port = port

    def toJson(self):
        return {
            'command': self.command,
            'server_port' : self.port
        }


class DownloadMessage(Message):
    def __init__(self, file_chunk, file_offset):
        super().__init__(Command.DOWNLOAD)
        self.file_chunk = file_chunk
        self.file_offset = file_offset
    
    def toJson(self):
        return {
            'command': self.command,
            'file_data': self.file_chunk,
            'file_offset': self.file_offset
        }

class UploadMessage(Message):
    def __init__(self, file_data, file_offset):
        super().__init__(Command.UPLOAD)
        self.file_data = file_data
        self.file_offset = file_offset
    
    def toJson(self):
        return {
            'command': self.command,
            'file_data': self.file_data,
            'file_offset': self.file_offset
        }

class ResponseUploadMessage(Message):
    def __init__(self, file_offset):
        super().__init__(Command.RESPONSE_UPLOAD)
        self.file_offset = file_offset

    def toJson(self):
        return {
            'command': self.command,
            'file_offset': self.file_offset
        }
    
class ConnectionDownloadMessage(Message):
    def __init__(self, file_name):
        super().__init__(Command.DOWNLOAD_CONECTION)
        self.file_name = file_name

    def toJson(self):
        return {
            'command': self.command,
            'file_name': self.file_name
        }
    
class ResponseConnectionDownloadMessage(Message):
    def __init__(self, server_port, file_size):
        super().__init__(Command.RESPONSE_DOWNLOAD_CONECTION)
        self.server_port = server_port
        self.file_size = file_size

    def toJson(self):
        return {
            'command': self.command,
            'server_port': self.server_port,
            'file_size' : self.file_size
        }
    
class StartDownloadMessage(Message):
    def __init__(self):
        super().__init__(Command.DOWNLOAD_START)

    def toJson(self):
        return {
            'command': self.command
        }

    
    