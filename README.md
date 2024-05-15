
## Correr Server
python3 start-server.py -v -s '/files/server' 

## Correr Client
python3 upload.py -v -s './files/client' -n 'Archivo.txt' 
python3 download.py -v -d './files/client' -n 'Archivo.txt'

python3 upload-selective-repeat.py -v -s './files/client' -n 'Archivo.txt'
python3 download-selective-repeat.py -v -d './files/client' -n 'Archivo.txt'

python3 upload.py -v -s './files/client' -n 'mininet.pdf' 
python3 upload-selective-repeat.py -v -s './files/client' -n 'mininet.pdf'
python3 download.py -v -d './files/client' -n 'mininet.pdf'
python3 download-selective-repeat.py -v -d './files/client' -n 'mininet.pdf'