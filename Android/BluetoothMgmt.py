import socket
import threading
import time
import multiprocessing

from env import *


class BluetoothMgmt(multiprocessing.Process):
    handle_q = multiprocessing.Manager().Queue()

    def __init__(self, job_q, header):
        multiprocessing.Process.__init__(self)

        self.header = header
        self.client = None
        self.job_q = job_q
        self.daemon = True

        self.start()

    def recv(self):
        while True:
            try:
                data = self.client.recv(ANDROID_BUFFER_SIZE)
                if not len(data):
                    continue
                packet = data.decode('utf-8').rstrip()

                print("[LOG][AND]", f"Received from Android: {packet}")
                self.job_q.put(f'{self.header}:{packet}\n')
                self.job_q.put(f'{self.header}:ALG:{packet}')

            except Exception as e:
                print("[ERR][AND]:",
                      "Failed to receive data. Bluetooth Disconnected")
                break

            time.sleep(0.00001)

        self.close_connection()

    def send(self, message):
        if(not self.client):
            print("[ERR][AND]:",
                  f"Trying to send packet {message} but no clients connected!")
        else:
            try:
                self.client.send(message)
                time.sleep(0.6)

            # will remove the try except, this one is needed because Nexus app and Bluetooth Terminal send in different format
            except:
                self.client.send((message).encode('utf-8'))
                time.sleep(0.6)

            print("[LOG][AND]:",
                  f'Sending "{message}" to Android successful')

    def close_connection(self):
        self.client.close()
        self.client = None
        print("[LOG][AND]", "Android Bluetooth Connection closed")

    def getPacketHeader(self):
        return self.header

    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize() != 0):
                packet, recv_from = self.handle_q.get()
                packet = packet.rstrip()
                self.send(f'{packet}')
                self.handle_q.task_done()
                print("[LOG][AND]",
                      f'Done Handling Packet from "{recv_from}" ,content: "{packet}"')
            time.sleep(0.000001)

    def handle(self, packet, recv_from):
        self.handle_q.put((packet, recv_from))

    def run(self):
        q_thread = threading.Thread(target=self.handleProcessor, args=())
        q_thread.start()

        server_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM,
                                    socket.BTPROTO_RFCOMM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((ANDROID_HOST_MAC, ANDROID_BLUETOOTH_PORT))
        server_sock.listen(ANDROID_BLUETOOTH_BACKLOG)

        while True:
            print("[LOG][AND]", "Listening for connection")
            self.client, address = server_sock.accept()
            print("[LOG][AND]", "Connection from: "+str(address))

            receive_thread = threading.Thread(target=self.recv, args=())
            receive_thread.start()
            receive_thread.join()

        self.close_connection()
        server_sock.close()
        q_thread.join()
