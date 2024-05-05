import os

def file_exists(absolute_path):
    return os.path.isfile(absolute_path)

def get_absolute_file_path(directory_path, file_name):
    return os.path.join(os.getcwd(), directory_path.lstrip('/'), file_name)

def get_file_size(directory_path):
    return os.path.getsize(directory_path)
