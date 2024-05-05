import argparse

class ParserArgument():
    
    def __init__(self):
        
        self.parser = argparse.ArgumentParser()
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(         "-v", "--verbose",
                                    help="increase output verbosity",
                                    dest="verbose",
                                    action='store_true')
        group.add_argument(         "-q", "--quiet",
                                    help="decrease output verbosity",
                                    dest="quiet",
                                    action='store_true')
        self.parser.add_argument(   "-H", "--host",
                                    help="server IP address",
                                    dest="host",
                                    metavar='ADDR',
                                    action='store',
                                    default="127.0.0.1",
                                    required=False)
        self.parser.add_argument(   "-p", "--port",
                                    help="server port",
                                    dest="port",
                                    type=int,
                                    action='store',
                                    default=8080,
                                    required=False)
    
    def getArgumentVerbose(self):
        return self.parser.parse_args().verbose
    
    def getArgumentQuit(self):
        return self.parser.parse_args().quit
    
    def getArgumentHost(self):
        return self.parser.parse_args().host
    
    def getArgumentPort(self):
        return self.parser.parse_args().port

class ParserArgumentServer(ParserArgument):
    
    def __init__(self):
        
        super().__init__()
        
        self.parser.add_argument(   "-s", "--storage", 
                                    help="storage dir path",
                                    dest="storage",
                                    type=str,
                                    metavar='FILE PATH',
                                    action='store',
                                    required=True)
    
    def getArgumentStoragePath(self):
        return self.parser.parse_args().storage    
       
class ParserArgumentUploadClient(ParserArgument):
    
    def __init__(self):
        
        super().__init__()
        
        self.parser.add_argument(   "-s", "--src", 
                                    help="source file path",
                                    dest="src",
                                    type=str,
                                    metavar='FILE PATH',
                                    action='store',
                                    required=True)
        self.parser.add_argument(   "-n", "--name", 
                                    help="file name",
                                    dest="name",
                                    type=str,
                                    metavar='FILE NAME',
                                    action='store',
                                    required=True)
    
    def getArgumentSource(self):
        return self.parser.parse_args().src
    
    def getArgumentName(self):
        return self.parser.parse_args().name
    
class ParserArgumentDownloadClient(ParserArgument):
    
    def __init__(self):
        
        super().__init__()
        
        self.parser.add_argument(   "-d", "--dst", 
                                    help="destination file path",
                                    dest="dst",
                                    type=str,
                                    metavar='FILE PATH',
                                    action='store',
                                    required=True)
        self.parser.add_argument(   "-n", "--name", 
                                    help="file name",
                                    dest="name",
                                    type=str,
                                    metavar='FILE NAME',
                                    action='store',
                                    required=True)
    
    def getArgumentDestination(self):
        return self.parser.parse_args().dst
    
    def getArgumentName(self):
        return self.parser.parse_args().name    