import socket
from websocket import WebSocketHandler
import numpy as np
import cv2
from PIL import Image
from scan import init,get_img,crop_image
from stitch import Stitcher

camera = cv2.VideoCapture(0)
class ScanSocketHandler(WebSocketHandler):
    def __init__(self, req, addr, server, H_horizontal_list,H_vertical_list):
        super(ScanSocketHandler, self).__init__(req, addr, server)
    	self.scan = False
    	self.H_horizontal_list = H_horizontal_list
        self.H_vertical_list = H_vertical_list
        self.stitcher = Stitcher()

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
            self.ser = init()
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
            #img = get_img(camera,i*10,j*10)
            # convert ndarray to str
            #img_str = cv2.imencode('.jpg', img)[1].tostring()
            
            # convert ndarray to PIL Image
            #OpenCV stores color image in BGR format. So, the converted PIL image is also in BGR-format. The standard PIL image is stored in RGB format. 
            RGBImg =  np.zeros(img.shape,img.dtype)
            RGBImg[:,:,0] = img[:,:,2]
            RGBImg[:,:,1] = img[:,:,1]
            RGBImg[:,:,2] = img[:,:,0]
            pil_img = Image.fromarray(RGBImg)
            
            # crop the image 
            crop_img = crop_image(pil_img)
            
            # convert PIL to opencv image
            open_cv_image = np.array(crop_img)  
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            self.imgs.append(open_cv_image)
            
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
                print(offset_y)
                img = img[offset_y:,:] 
                self.result.append(img)
            
           
            if len(self.result) > 1:
                if x == 9:
                    self.height = self.result[0].shape[0]
                    self.result = [self.result[1]]
                elif x == 18:
                    self.height = self.stitch_img.shape[0]
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
                    
                    self.stitch_img[0:stitch_img.shape[0],0:stitch_img.shape[1]] = stitch_img

                #img_str = cv2.imencode('.jpg', img)[1].tostring()
                cv2.imwrite("stitch.jpg",self.stitch_img)
                img_str = cv2.imencode('.jpg', self.stitch_img)[1].tostring()


                self.send_binary(img_str)
            #img_str = merge_img.tobytes("jpeg","RGB")
            

            self.send_text(str(x) + " " + str(y))

        if(text == "cancel"):
            self.scan = False
            merge_img = 0
            


    def on_binary_message(self, buf):
        print(buf)
        self.send_binary(buf)
