from select import select
import serial
import cv2
import time
import numpy as np
from PIL import Image
import time
def init():
	
	'''
	camera = cv2.VideoCapture(0)
	print("finish camera")
	camera.set(3,1024)
	camera.set(4,768)
	camera.set(5,30)
	camera.set(15, -8)
	'''
	
	ser = serial.Serial(timeout=0.2)
	ser.port = '/dev/cu.wchusbserial1410'
	ser.baudrate = 115200
	ser.open()
	print(ser.is_open)
	time.sleep(3)
	ser.write(b'G28\n')
	line = ser.readline()
	print(line)
	while(1):
		line = ser.readline()
		if line == b'ok\n':
			break
	
	
	return ser


def crop_image(img):
	print(img.size)
	img = img.crop((120,60,1160,660))
	return img

def get_img(camera,ser,x,y):
	x = 30 + x	
	y = 160 - y
	cmd = "G1 F8000 X" + str(x) + " Y" + str(y) + "\n"
	print(cmd)	
	ser.write(str.encode(cmd))
	while (1):
		line = ser.readline()
		if line == b'ok\n':
			break
	if(y == 160):
		time.sleep(3)
	else:
		time.sleep(0.4)
	ret,frame = camera.read()
	
	return frame 




'''
for x in range(1,10,1):
	for y in range(1,10,1):
		move_x = x * 10 
		move_y = y * 10 
		cmd = "G1 F2000 X" + str(move_x) +" Y" + str(move_y) + "\n"
		ser.write(str.encode(cmd))
		while(1):
			line = ser.readline()
			if line == b'ok\n':
				break
		time.sleep(1)
		ret, frame = camera.read()
		cv2.imwrite("image/" + str(move_x) + "+" +  str(move_y) + ".jpg",frame)
		

camera.release()
'''
