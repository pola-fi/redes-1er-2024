
## Correr Server
python3 start-server.py -s '/files/server'

## Correr Client
python3 upload.py -s './files/client' -n 'Archivo.txt' 
python3 download.py -d './files/client' -n 'Archivo.txt'