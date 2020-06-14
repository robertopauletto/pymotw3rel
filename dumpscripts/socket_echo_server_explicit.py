# socket_echo_server_explicit.py

import socket
import sys

# Crea un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Collega il socket all'indirizzo ricevuto da riga di comando
server_name = sys.argv[1]
server_address = (server_name, 10000)
print('in avvio su {} porta {}'.format(*server_address))
sock.bind(server_address)
sock.listen(1)

while True:
    print('in attesa di una connessione')
    connection, client_address = sock.accept()
    try:
        print('client connesso:', client_address)
        while True:
            data = connection.recv(16)
            print('ricevuto {!r}'.format(data))
            if data:
                connection.sendall(data)
            else:
                break
    finally:
        connection.close()
