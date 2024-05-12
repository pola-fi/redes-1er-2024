from lib.client.client import Client
from lib.ParserArguments import ParserArgumentDownloadClient
from lib.utilities.file_utilities import get_absolute_file_path
from lib.file import File

if __name__ == "__main__":
    
    parser_arguments = ParserArgumentDownloadClient()
    client = Client(parser_arguments.getArgumentHost(), 
                    parser_arguments.getArgumentPort(),
                    parser_arguments.getArgumentVerbose(),
                    parser_arguments.getArgumentQuit())

    file_name = parser_arguments.getArgumentName()
    directory_of_file_relative_path = parser_arguments.getArgumentDestination()
    
    file = File(get_absolute_file_path(directory_of_file_relative_path, file_name), file_name)

    file_size = client.download_open_conection(file)
    client.download_file(file, file_size)