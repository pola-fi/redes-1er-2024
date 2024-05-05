from lib.server.server import Server
from lib.ParserArguments import ParserArgumentServer

if __name__ == "__main__":
    
    parser_arguments = ParserArgumentServer()
    server = Server(parser_arguments.getArgumentHost(), parser_arguments.getArgumentPort(), parser_arguments.getArgumentStoragePath())
    server.listen()