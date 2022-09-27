from sqlite3 import connect
from env import *
import serial
import threading
import multiprocessing
import time


class RCMgmt(multiprocessing.Process):
    handle_q = multiprocessing.Manager().Queue()

    print_lock = threading.Lock()
    serial_port = serial.Serial()
    connected = False

    def __init__(self, job_q, header):
        multiprocessing.Process.__init__(self)
        self.job_q = job_q
        self.header = header
        self.serial_port.baudrate = CAR_BAUD_RATE
        self.serial_port.port = CAR_PORT
        self.serial_port.timeout = CAR_TIMEOUT
        self.daemon = True

        self.start()

    def connect(self):
        # If it is currently open, close the current connection and re-open
        if self.serial_port.isOpen():
            self.serial_port.close()
        try:
            self.serial_port.open()
            self.connected = True
            print("[LOG][STM]", "RC-Car Connection opened")
            return True
        except serial.SerialException as e:
            print("[ERR][STM]", "Unable to open serial port")
            return False

    def close_connection(self):
        self.serial_port.close()
        print("[LOG][STM]", "RC-Car Connection closed")

    def getPacketHeader(self):
        return self.header

    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize() != 0):
                packet, recv_from = self.handle_q.get()
                packet = packet.rstrip()
                self.write(packet)
                self.handle_q.task_done()
                print("[LOG][STM]",
                      f'Done Handling Packet from "{recv_from}" ,content: "{packet}"')

            time.sleep(0.000001)

    def handle(self, packet, recv_from):
        self.handle_q.put((packet, recv_from))

    def write(self, message):
        if self.serial_port.isOpen():
            message = message.rstrip()
            for c in message:
                self.serial_port.write(c.encode('utf-8'))
            print("[LOG][STM]:", f'Sending "{message}" to RC-Car')
        else:
            print("[ERR][STM]:", "Writing failed! Serial port not open")

    def read(self, job_q):
        while True:
            try:
                data = self.serial_port.readline().rstrip()  # non-blocking

                if len(data) == 0:
                    continue
                data = data.decode('utf-8')
                print("[LOG][STM]:",
                      f'Receiving raw data from RC-Car: {data}')

                for rec in CAR_RECIVER_ID:
                    job_q.put(f'{self.header}:{rec}:{data}\n')

                print("[LOG][STM]:",
                      f'Finished sending data from RC-Car to {CAR_RECIVER_ID}')

            except serial.SerialException as e:
                print("[ERR][STM]:", "Reading failed! Serial port not open")
                while not self.connect():
                    print("[LOG][STM]:", "Reconnecting STM in 3 seconds...")
                    time.sleep(3)

            time.sleep(0.000001)

    def run(self):
        while (self.connect() != True):
            print("[LOG][STM]:", "Reconnecting STM in 3 seconds...")
            time.sleep(3)

        t1 = threading.Thread(target=self.read, args=(self.job_q,))
        t2 = threading.Thread(target=self.handleProcessor, args=())

        t1.start()
        t2.start()

        t1.join()
        t2.join()
