from select import select
import serial
import cv2
import time
import numpy as np
def init():
	print("init")
	'''
	camera = cv2.VideoCapture(0)
	print("finish camera")
	camera.set(3,1024)
	camera.set(4,768)
	camera.set(5,30)
	camera.set(15, -8)
	'''
	'''
	ser = serial.Serial(timeout=0.2)
	ser.port = '/dev/cu.wchusbserial1410'
	ser.baudrate = 250000
	ser.open()
	select((ser.fileno(), ), (), ())
	ser.write(b'G28\n')
	
	while(1):
		line = ser.readline()
		if line == b'ok\n':
			break
	'''
	
	return camera




def get_sub_frame(frame,x_min,x_max,y_min,y_max):
    sub_frame = np.zeros((x_max-x_min,y_max-y_min,3)) 
    # frame shape 720, 1280
    for channel in range(3):
        for x in range(x_min,x_max,1):
            for y in range(y_min,y_max,1):
                sub_frame[x-x_min][y-y_min][channel] = frame[x][y][channel]  
    return sub_frame


def get_img(camera,x,y):
	
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
