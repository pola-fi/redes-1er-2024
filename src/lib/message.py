from lib.command import Command

class Message:
    def __init__(self, command):
        self.command = command

class ConnectionMessage(Message):
    def __init__(self, file_name ,file_size):
        super().__init__(Command.CONNECTION)
        self.file_size = file_size
        self.file_name = file_name
    
    def toJson(self):
        return {
            'command': self.command,
            'file_size': self.file_size
        }

class DownloadMessage(Message):
    def __init__(self, file_path):
        super().__init__(Command.DOWNLOAD)
        self.file_path = file_path

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
    
    