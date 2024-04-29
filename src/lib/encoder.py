import json

class Encoder:
    def encode(self, message):
        return json.dumps(message).encode()
    
    def decode(self, message):
        return json.loads(message)
