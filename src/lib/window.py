import threading

class Window:
    def __init__(self, max_size, chunk_size):
        self.data = []
        self.max_size = max_size
        self.last = -1 * chunk_size
        self.chunk_size = chunk_size
        self.last_sended = -1 * chunk_size
        self.last_received = -1 * chunk_size
        self.lock = threading.Lock()

    def next_sent_element(self):
        with self.lock:
            return self.last_sended + self.chunk_size

    def add(self, element):
        
        # Agregar elemento al final de la ventana
        with self.lock:
            self.data.append(element)

    def remove(self, element):
        
        with self.lock:
        # Sacar el elemento especificado de la ventana, si está presente
            if element in self.data:
                self.data.remove(element)

    def remove_first(self):
        with self.lock:
            # Sacar el elemento especificado de la ventana, si está presente
            if self.data:
                return self.data.pop(0)
        
    def is_full(self):
        with self.lock:
            # Sacar el elemento especificado de la ventana, si está presente
            if len(self.data) == self.max_size:
                return True
            else:
                False
        
    def is_empty(self):
        with self.lock:
            if len(self.data) == 0:
                return True
            else:   
                return False
        
    def remove_all(self):
        with self.lock:
            self.data = []

    def size(self):
        with self.lock:
            return len(self.data)
        
    def is_first(self, element):
        with self.lock:
            if self.data[0] == element:
                return True
            else:   
                return False
    
    def has_space(self):
        with self.lock:
            return len(self.data) < self.max_size

    def __str__(self):
        return str(self.data)