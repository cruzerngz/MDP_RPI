import time
import socket
import imagezmq
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
from getkey import getkey, keys
from env import *

def take_photo(camera):
	try:
		print('entered camera..')
		#camera.capture(f"rpi_sent_{counter}.jpg")
		#image =  open('rpi_sent_1.jpg','wb')
		#camera.capture(image)
		#counter += 1
		print('1')
		rawCapture = PiRGBArray(camera)
		print('2')
		camera.capture(rawCapture,'bgr')
		print('3')
		image = rawCapture.array
		print('Image captured.')
	except Exception as e:
		print(f"Error! failed to capture Image: {str(e)}")
	return image

def process_image(image):
	image_sender = imagezmq.ImageSender(connect_to = CAMERA_PROCESSING_ADDRESS)
	rpiName = socket.gethostname()

	print('sending for processing..')
	imageID = image_sender.send_image(rpiName, image)
	print('image returned from processing')

	return imageID

if __name__ == "__main__":
	print('Initalising PiCamera..')
	camera = PiCamera()
	camera.resolution = (CAMERA_RESOLUTION_X, CAMERA_RESOLUTION_Y)
	time.sleep(2)
	print('PiCamera is ready. Press [ENTER] to take photo.')

	key = getkey()
	while key == keys.ENTER:
		image = take_photo(camera)
		imageID = process_image(image)
		imageID = imageID.decode('UTF-8')
		print('Image ID: ' + imageID)
		print('Press [ENTER] to take photo, any key to terminate.')
		key = getkey()


	image_sender = imagezmq.ImageSender(connect_to = CAMERA_PROCESSING_ADDRESS)
	doneimage = take_photo(camera)
	response = image_sender.send_image('DONE', doneimage)
	response = response.decode('UTF-8')
	if(response == 'byebye'):
		print('yolov5 terminated, collage generated on Mac')

	print('terminating camera..')
	camera.close()

