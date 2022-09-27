import multiprocessing
import time

from Networking import PacketHandler
from Android import BluetoothMgmt
from RemoteControlCar import RCMgmt
from TerminalInput import TerminalMgmt
from PiCamera import CameraMgmt
from SocketServer import SocketServer

from env import *

# Create multi-thread process queue
process_Queue = multiprocessing.Manager().Queue()


# Create Threads
bluetoothMgmt = BluetoothMgmt.BluetoothMgmt(process_Queue, "AND")
rcMgmt = RCMgmt.RCMgmt(process_Queue, "STM")
cameraMgmt = CameraMgmt.CameraMgmt(process_Queue, "IMG")
algoMgmt = SocketServer.SocketServerMgmt(
    process_Queue, "ALG", SERVER_IP_ADDRESS, SERVER_PORT, SERVER_BUFFER_SIZE)


# Create Packet Handler to identify different services in queue
packetHandler = PacketHandler.PacketHandler()
packetHandler.registerHandler(bluetoothMgmt)
packetHandler.registerHandler(rcMgmt)
packetHandler.registerHandler(cameraMgmt)
packetHandler.registerHandler(algoMgmt)


# handling packet
def handle_packet():
    while True:
        time.sleep(0.001)
        if(process_Queue.qsize() != 0):
            packetHandler.handle(process_Queue.get())


pakcet_handling_process = multiprocessing.Process(
    target=handle_packet, args=())
pakcet_handling_process.start()


# handling terminal input
# def push_to_q(message):
#     process_Queue.put(message)
# terminal_input = TerminalMgmt.TerminalMgmt(push_to_q)
# terminal_input.startIO()


# cleaning up
# pakcet_handling_process.terminate()
pakcet_handling_process.join()
