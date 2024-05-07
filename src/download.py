from lib.client.client import Client
from lib.ParserArguments import ParserArgumentDownloadClient
from lib.utilities.file_utilities import get_absolute_file_path

if __name__ == "__main__":
    
    parser_arguments = ParserArgumentDownloadClient()
    client = Client(parser_arguments.getArgumentHost(), parser_arguments.getArgumentPort())

    file_name = parser_arguments.getArgumentName()
    directory_of_file_relative_path = parser_arguments.getArgumentDestination()

    file_absolute_path = get_absolute_file_path(directory_of_file_relative_path, file_name)
    
    client.download_open_conection(file_name)
    client.download_file(file_absolute_path)