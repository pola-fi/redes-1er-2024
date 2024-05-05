from lib.client.client import Client
from lib.client.ParserArguments import ParserArgumentUploadClient

if __name__ == "__main__":
    
    parser_arguments = ParserArgumentUploadClient()
    client = Client(parser_arguments.getArgumentHost(), parser_arguments.getArgumentPort())
    client.open_conection(parser_arguments.getArgumentSource(), parser_arguments.getArgumentName())
    client.upload_file(parser_arguments.getArgumentSource(), parser_arguments.getArgumentName())