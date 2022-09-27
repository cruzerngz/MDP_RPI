import multiprocessing
from struct import pack
import time
import threading
import socket
import imagezmq
from picamera import PiCamera
from picamera.array import PiRGBArray
from env import *


class CameraMgmt(multiprocessing.Process):
    handle_q = multiprocessing.Manager().Queue()

    def __init__(self, job_q, header):
        multiprocessing.Process.__init__(self)
        self.job_q = job_q
        self.header = header
        self.daemon = True
        self.camera = None
        self.image_sender = None

        self.start()

    def getPacketHeader(self):
        return self.header

    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize() != 0):
                packet, recv_from = self.handle_q.get()
                packet = packet.rstrip()

                self.write(packet)
                self.handle_q.task_done()
                print("[LOG][IMG]:",
                      f'Done Getting Image ID requested by "{recv_from}"')

            time.sleep(0.000001)

    def handle(self, packet, recv_from):
        self.handle_q.put((packet, recv_from))

    def write(self, message):
        try:
            image = self.take_photo()
            print("[LOG][IMG]:", f'Capturing image successful. Processing image')
            if message == 'DONE':
                imageDetails = self.process_image(image, 'DONE')
                print("[LOG][IMG]:",
                  f'Yolov5 terminated! collage generated on Mac. Response: {imageDetails}')
                return
            rpiName = socket.gethostname()
            imageDetails = self.process_image(image, rpiName)
            print("[LOG][IMG]:",
                  f'Processing successfull. Image Details: {imageDetails}')
            self.read(imageDetails)

        except:
            print("[ERR][IMG]:", f'Image recognition failed! Terminating camera...')
            self.camera.close()

    def read(self, message):
        try:
            for rec in CAMERA_RECEIVER:
                self.job_q.put(f'{self.header}:{rec}:{message}\n')
            print("[LOG][IMG]:",
                  f'Finished sending image data to {CAR_RECIVER_ID}')
        except:
            print("[ERR][IMG]:",
                  f"Sending image data to {CAMERA_RECEIVER} failed!")

    def take_photo(self):
        try:
            rawCapture = PiRGBArray(self.camera)
            print("[LOG][IMG]:", 'Entered camera successfully')
            self.camera.capture(rawCapture, 'bgr')
            image = rawCapture.array
            print("[LOG][IMG]:", 'Image captured successfully')
        except Exception as e:
            print("[ERR][IMG]:", f"Failed to capture Image!")
        return image

    def process_image(self, image, rpiName):
        print("[LOG][IMG]:", 'Sending for processing')
        imageDetails = self.image_sender.send_image(rpiName, image).decode('UTF-8')
        return imageDetails

    def run(self):
        print("[LOG][IMG]:", 'Initalising PiCamera')
        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = (CAMERA_RESOLUTION_X, CAMERA_RESOLUTION_Y)
        time.sleep(2)
        print("[LOG][IMG]:", 'PiCamera is ready. Waiting for command to take photo')
        
        print("[LOG][IMG]:", 'Trying to connect to image processing server')
        self.image_sender = imagezmq.ImageSender(
            connect_to=CAMERA_PROCESSING_ADDRESS)
        print("[LOG][IMG]:", 'Connection to image processing server successful')

        t2 = threading.Thread(target=self.handleProcessor, args=())
        t2.start()
        t2.join()
