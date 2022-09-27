import socket
import multiprocessing
from time import sleep
from env import *

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (SERVER_IP_ADDRESS, SERVER_PORT)
print(f'starting up on {server_address[0]} port {server_address[1]}')
sock.connect(server_address)


def listen():
    while True:
        try:
            data = sock.recv(SERVER_BUFFER_SIZE)
            print('\nreceived: ', data.decode('utf-8'))

        except:
            print('closing socket')
            sock.close()
            break

        sleep(0.001)


if __name__ == '__main__':
    t = multiprocessing.Process(target=listen, args=())
    t.start()

    while True:
        try:
            message = f'{input()}'
            print('sending: ', message)
            sock.send(message.encode('utf-8'))

        except:
            print('closing socket')
            sock.close()
            break

    t.join()
