from lib.client.client import Client


if __name__ == "__main__":
    client = Client("127.0.0.1", 8080)
    client.open_conection()
    client.upload_file("Archivo.txt")