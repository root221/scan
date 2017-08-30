import socket
from websocket import WebSocketHandler
import numpy as np
import cv2
from scan import init,get_img
from stitch import Stitcher
import pickle
camera = cv2.VideoCapture(0)
f = open("data/calibration.p","rb")
homograpy = pickle.load(f)['mtx']
class ScanSocketHandler(WebSocketHandler):
    def __init__(self, req, addr, server, H_horizontal_list,H_vertical_list,ser_port,ser_baudrate,output_filename="result.jpg"):
        super(ScanSocketHandler, self).__init__(req, addr, server)
    	self.scan = False
    	
        self.H_horizontal_list = H_horizontal_list
        self.H_vertical_list = H_vertical_list
        self.stitcher = Stitcher()
        self.output_filename = output_filename

        self.ser_port = ser_port
        self.ser_baudrate = ser_baudrate
    def serve_forever(self):
        #try:
        while True:
            try:
                self.do_recv()
            except socket.error as e:
                if e.errno == EAGAIN:
                    pass
                else:
                    print("socket error", e)
                    raise
        #except Exception as e:
        #    print("Error", e)

    def on_text_message(self, text):
        
        if(text == "scan"):
            self.result = []
            self.ser = init(self.ser_port,self.ser_baudrate)
            self.imgs = []           
            self.height = 0 
            self.stitch_img = np.zeros((5469, 3262, 3),dtype="uint8")
            self.send_text("start scanning")
        
        if(text[0:10] == "get image "):
            text = text[10:]
            x,y = text.split(" ")
            x = int(x)
            y = int(y) 
            img = get_img(camera,self.ser,x*10,y*10)
            
            # crop the image
            img = img[60:660,120:1160]
            
            self.imgs.append(img)
            
            # stitch image
            
            if len(self.imgs) > 1 and y <= 14:
                img,offset_y = self.stitcher.stitch(self.imgs[0],self.imgs[1],"horizontal",self.H_horizontal_list[y-1])
                print(img.shape)
                self.imgs = [img]    
            
            # return the result to front-end 
            if(x==0):
                self.stitch_img = np.zeros((5469, 3262, 3),dtype="uint8")
                img = self.imgs[0]
                self.stitch_img[0:img.shape[0]-68,0:img.shape[1]] = img[68:,:]
                img_str = cv2.imencode('.jpg', self.stitch_img)[1].tostring()
                self.send_binary(img_str)
            
            if(y == 14):
                self.imgs = []
                img = img[offset_y:,:] 
                self.result.append(img)
            
           
            if len(self.result) > 1:
                if x == 9:
                    self.height = self.result[0].shape[0]
                    self.result = [self.result[1]]
                elif x == 18:
                    #self.height = self.stitch_img.shape[0]
                    self.result = [self.result[1]]
                else:
                    img,offset_y = self.stitcher.stitch(self.result[0],self.result[1],"vertical",self.H_vertical_list[x-1])
                    self.result = [img] 
                     
                # return the result to front-end 
                if x < 9:
                    self.stitch_img[0:img.shape[0],:,:] = img
                
                else:
                    if x < 18:
                        stitch_img,offset_y = self.stitcher.stitch(self.stitch_img[0:self.height,:,:],img,"vertical",self.H_vertical_list[8])
                    else:
                        stitch_img,offset_y = self.stitcher.stitch(self.stitch_img[0:self.height,:,:],img,"vertical",self.H_vertical_list[17])
                    
                    if x == 17:
                        self.height = stitch_img.shape[0]
                    self.stitch_img[0:stitch_img.shape[0],0:stitch_img.shape[1]] = stitch_img

                img_str = cv2.imencode('.jpg', self.stitch_img)[1].tostring()


                self.send_binary(img_str)
            
            if(x<27):
                self.send_text(str(x) + " " + str(y))

            # finish scanning
            else:
                self.send_text("finish scanning")
                # calibrate the image
                bottom_left = np.dot(homograpy,np.array([0,self.stitch_img.shape[0],1])) 
                bottom_left = bottom_left / bottom_left[-1]
                bottom_right = np.dot(homograpy,np.array([self.stitch_img.shape[1],self.stitch_img.shape[0],1]))
                bottom_right = bottom_right / bottom_right[-1]
                stitch_img = cv2.warpPerspective(self.stitch_img,homograpy,(int(bottom_right[0]),int(bottom_right[1])))
                # crop the black region
                stitch_img = stitch_img[:int(bottom_left[1]),int(bottom_left[0]):]
                cv2.imwrite(self.output_filename,stitch_img)
        
        if(text == "cancel"):
            self.scan = False
            merge_img = 0
            


    def on_binary_message(self, buf):
        print(buf)
        self.send_binary(buf)
