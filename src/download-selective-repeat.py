from lib.client.client import Client
from lib.ParserArguments import ParserArgumentDownloadClient
from lib.utilities.file_utilities import get_absolute_file_path

if __name__ == "__main__":

    parser_arguments = ParserArgumentDownloadClient()

    client = Client(parser_arguments.getArgumentHost(),
                    parser_arguments.getArgumentPort(),
                    parser_arguments.getArgumentVerbose(),
                    parser_arguments.getArgumentQuit())
    client.download_open_conection(parser_arguments.getArgumentName())
    #client.download_file('/files/client','Archivo.txt')