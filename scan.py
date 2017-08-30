from select import select
import serial
import cv2
import time
import numpy as np
from PIL import Image
import time
def init(ser_port,ser_baudrate):
	
	# camera = cv2.VideoCapture(0)
	
	ser = serial.Serial(timeout=0.2)
	ser.port = ser_port
	ser.baudrate = ser_baudrate
	ser.open()
	
	time.sleep(3)
	ser.write(b'G28\n')
	line = ser.readline()
	
	while(1):
		line = ser.readline()
		if line == b'ok\n':
			break
	
	return ser

def get_img(camera,ser,x,y):
	x = 30 + x	
	y = 160 - y
	cmd = "G1 F7000 X" + str(x) + " Y" + str(y) + "\n"
	print(cmd)	
	ser.write(str.encode(cmd))
	while (1):
		line = ser.readline()
		if line == b'ok\n':
			break
	if(y == 160):
		time.sleep(3)
	else:
		time.sleep(0.5)
	ret,frame = camera.read()
	
	return frame 



