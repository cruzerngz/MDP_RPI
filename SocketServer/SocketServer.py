import socket
import threading
import time
import multiprocessing

from env import *


class SocketServerMgmt(multiprocessing.Process):
    handle_q = multiprocessing.Manager().Queue()

    def __init__(self, job_q, header, address, port, buffer_size):
        multiprocessing.Process.__init__(self)

        self.header = header
        self.address = address
        self.port = port
        self.buffer_size = buffer_size
        self.client = {}
        self.threads = {}
        self.job_q = job_q
        self.daemon = True

        self.start()

    def make_connection(self, sock):
        while True:
            new_client, address = sock.accept()
            if new_client:
                self.client[address] = new_client
                print(f"[LOG][{self.header}]",
                      f'connection with client "{address}" created!')
                receive_thread = threading.Thread(
                    target=self.recv, args=(address,))
                self.threads[address] = receive_thread

                receive_thread.start()
            time.sleep(0.1)

        for addr in self.threads:
            if self.threads[addr]:
                self.threads[addr].join()

    def recv(self, addr):
        while True:
            try:
                if addr not in self.client or not self.client[addr]:
                    print(
                        f"[ERR][{self.header}]: Client {addr} Not Exist.")
                    break

                data = self.client[addr].recv(self.buffer_size)
                if not len(data):
                    continue
                packet = data.decode('utf-8').rstrip()
                print(f"[LOG][{self.header}]: Received from {self.header} Server: " + packet)

                self.job_q.put(f'{self.header}:{packet}\n')

            except Exception as e:
                print(
                    f"[ERR][{self.header}]: Client {addr} Disconnected. Client is removed.")
                break

            time.sleep(0.00001)

        self.close_one_connection(addr)

    def send(self, message):
        if(not self.client):
            print(f"[LOG][{self.header}]:",
                  "Trying to send but no clients connected")
        else:
            inactive = []
            for addr in self.client:
                if not self.client[addr]:
                    continue
                try:
                    self.client[addr].send((message).encode('utf-8'))
                    print(f"[LOG][{self.header}]:", f'Sending {message} to {addr} successful!')
                    time.sleep(0.1)

                except:
                    print(
                    f"[ERR][{self.header}]: Client {addr} Disconnected. Client is removed.")
                    inactive.append(addr)
            
            for addr in inactive:
                self.close_one_connection(addr)

    def close_connection(self):
        for addr in self.client:
            self.close_one_connection(addr)
        print(f"[LOG][{self.header}]:",
              f'Successfully closing all client connections.')

    def close_one_connection(self, addr):
        try:
            self.client[addr].close()
            self.client[addr] = None
            self.threads[addr] = None
            
            print(f"[LOG][{self.header}]:",
                  f'Close client socket with address "{addr}" successful.')
        except:
            print(f"[ERR][{self.header}]:",
                  f'Closing client with address "{addr}" failed!')

    def getPacketHeader(self):
        return self.header

    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize() != 0):
                packet, recv_from = self.handle_q.get()
                packet = packet.rstrip()
                self.send(f'{recv_from}:{packet}')
                self.handle_q.task_done()
            time.sleep(0.000001)

    def handle(self, packet, recv_from):
        self.handle_q.put((packet, recv_from))

    def run(self):
        q_thread = threading.Thread(target=self.handleProcessor, args=())
        q_thread.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.address, self.port)
        print(f"[LOG][{self.header}]:",
              f'Starting up on {server_address[0]} port {server_address[1]}')
        sock.bind(server_address)
        sock.listen()

        binder_thread = threading.Thread(
            target=self.make_connection, args=(sock,))
        # receive_thread = threading.Thread(target=self.recv, args=(sock,))

        binder_thread.start()
        # receive_thread.start()

        binder_thread.join()
        # receive_thread.join()

        self.close_connection()
        sock.close()
        q_thread.join()
