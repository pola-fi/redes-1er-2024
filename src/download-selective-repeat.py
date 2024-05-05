from lib.client.client import Client

if __name__ == "__main__":
    client = Client("127.0.0.1", 8080)
    client.download_open_conection('Archivo.txt')
    #client.download_file('/files/client','Archivo.txt')