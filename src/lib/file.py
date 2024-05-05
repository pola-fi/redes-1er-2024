from lib.utilities.file_utilities import get_file_size

class File():
    def __init__(self, absolute_path, name):
        self.absolute_path = absolute_path
        self.name = name
        self.size = get_file_size(absolute_path)