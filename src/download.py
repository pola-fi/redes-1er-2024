from lib.client.client import Client
from lib.ParserArguments import ParserArgumentDownloadClient

if __name__ == "__main__":
    
    parser_arguments = ParserArgumentDownloadClient()
    client = Client(parser_arguments.getArgumentHost(), parser_arguments.getArgumentPort())
    client.download_open_conection(parser_arguments.getArgumentName())
    client.download_file(parser_arguments.getArgumentDestination(),parser_arguments.getArgumentName())