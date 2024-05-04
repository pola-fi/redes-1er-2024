from lib.client.client import Client
from lib.client.ParserArgumentClient import ParserArgumentClient

if __name__ == "__main__":
    
    parser_argument = ParserArgumentClient()
    client = Client(parser_argument.getArgumentHost(), parser_argument.getArgumentPort())
    client.open_conection(parser_argument.getArgumentSource(), parser_argument.getArgumentName())
    client.upload_file(parser_argument.getArgumentSource(), parser_argument.getArgumentName())