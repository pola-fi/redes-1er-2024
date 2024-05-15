from lib.utilities.file_utilities import get_file_size
from lib.utilities.file_utilities import file_exists
import os

class File():
    def __init__(self, absolute_path, name):
        self.absolute_path = absolute_path
        self.name = name

    def create(self):
        if file_exists(self.absolute_path):
            os.remove(self.absolute_path)
        try:             
            with open(self.absolute_path, "w") as f:
                f.close()
            
        except Exception as e:
            print("Ocurrió un error al intentar crear o cerrar el archivo:", e)

    def get_size(self):
        return get_file_size(self.absolute_path)
    
    def write(self, data, offset):
        if file_exists(self.absolute_path):
            with open(self.absolute_path, 'r+b') as file:
                file.seek(offset)
                file.write(data)
        else:
            print(f"file:{self.absolute_path} doesn't exist")
