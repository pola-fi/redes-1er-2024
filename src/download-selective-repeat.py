from lib.client.client import Client
from lib.ParserArguments import ParserArgumentDownloadClient
from lib.utilities.file_utilities import get_absolute_file_path

if __name__ == "__main__":

    parser_arguments = ParserArgumentDownloadClient()

    client = Client("127.0.0.1", 8080)
    client.download_open_conection('Archivo.txt')
    #client.download_file('/files/client','Archivo.txt')