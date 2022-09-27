import os
import env
from env import *


class PacketHandler:

    def __init__(self):
        self.handlers = {}

    def registerHandler(self, instance):
        unique_id = instance.getPacketHeader()
        if unique_id not in self.handlers:
            self.handlers[unique_id] = instance
        else:
            print("[ERR][NET]:",
                  "Failed to register handler, please choose another unique_id")

    def unregisterHandler(self, unique_id):
        try:
            del self.handlers[unique_id]
        except KeyError:
            print("Fail to remove, handler not found.")

    # def convertToName(self, header):
    #     if header in NETWORKING_PACKAGE_NAMING:
    #         return NETWORKING_PACKAGE_NAMING[header]
    #     return NETWORKING_PACKAGE_NAMING['OTH']

    def handle(self, packet):
        splitData = packet.split(':')
        if len(splitData) > 2:
            recv_from = splitData[0]
            unique_id = splitData[1]
            data = ':'.join(splitData[2:]).rstrip()

            if unique_id in self.handlers:
                self.handlers[unique_id].handle(data, recv_from)
                print("[LOG][NET]:", f'Processing request: {packet.rstrip()}')
            else:
                print("[ERR][NET]:",
                    f'Failed to get destination "{unique_id}" for: {packet.rstrip()}')
        else:
            print("[ERR][NET]:", f'Failed to process request: {packet.rstrip()}')
