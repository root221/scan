
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from hashlib import sha1
from errno import EAGAIN
import SocketServer
import socket
import base64
import cv2

import numpy as np

from websocket import WebSocketHandler, MAGIC_STRING
from scan import init,get_img,crop_image
from stitch import stitch
from PIL import Image
camera = cv2.VideoCapture(0)
#camera.set(3,1280)
#camera.set(4,720)
#camera.set(3,1024)
#camera.set(4,768)
#camera.set(5,30)
#camera.set(15, -8)

width = 90
height = 60

global scan 
global stitch_img
global ser  
global imgs
global height
class MyWebsocketHandler(WebSocketHandler):
    def serve_forever(self):
        try:
            while True:
                try:
                    self.do_recv()
                except socket.error as e:
                    if e.errno == EAGAIN:
                        pass
                    else:
                        print("socket error", e)
                        raise
        except Exception as e:
            print("Error", e)

    def on_text_message(self, text):
        if(text == "scan"):
            print(text)
            global result
            result = []
            global scan
            scan = True
            #global merge_img
            #merge_img = Image.new('RGB',(170 * 10,200 * 10),(255,255,255))
            global stitch_img
            stitch_img = np.zeros((5000, 3297, 3),dtype="uint8")
            global imgs
            imgs = []
            global ser
            ser = init()
            global height
            height = 0
            self.send_text("start scanning")
        
        if(text[0:10] == "get image "):
            
            text = text[10:]
           
            x,y = text.split(" ")
            x = int(x)
            y = int(y) 
            img = get_img(camera,ser,x*10,y*10)
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
            cv2.imwrite(str(y) + ".jpg",open_cv_image)
            imgs.append(open_cv_image)
            
            # stitch image
            
            if len(imgs) > 1 and y <= 14:            
                (img,offset_y) = stitch(imgs,"horizontal",y-1,x)
                #img = img[offset_y:,:]
                #cv2.imwrite("test.jpg",img)
                imgs = [img]    
            
            
            if(x==0):
                stitch_img = np.zeros((5000, 3297, 3),dtype="uint8")
                stitch_img[0:img.shape[0],0:img.shape[1]] = img
                img_str = cv2.imencode('.jpg', stitch_img)[1].tostring()
                self.send_binary(img_str)
            if(y == 14):
                imgs = []
                img = img[offset_y:,:] 
                cv2.imwrite("test.jpg",img)
                result.append(img)
            
            # stitch image from left to right
            '''
            if(len(imgs) * 10 == width):
                imgs = imgs[::-1]
                img = stitch(imgs,"horizontal")
                result.append(img)
                imgs = []
                # return the result to front-end when there is one image
                if(len(result) == 1):
                    img_str = cv2.imencode('.jpg', img)[1].tostring()
                
                #self.send_binary(img_str)
            '''
            if(len(result) > 1 and x < 9):
                print(x) 
                #self.send_text(str(x) + " " + str(y))
                img,offset_y = stitch(result,"vertical",0,x-1)
                cv2.imwrite("result1.jpg",img)
                result = [img]
                
                
                # return the result to front-end 
                #if x < 14:
                #    stitch_img[0:img.shape[0],:,:] = img
                  
                #else:
                #    a = [stitch_img[0:height,:,:],img]
                #    stitch_img,offset_y = stitch(a,"vertical",0,100)
                    
                    
                img_str = cv2.imencode('.jpg', img)[1].tostring()

                self.send_binary(img_str)
            #img_str = merge_img.tobytes("jpeg","RGB")
            

            self.send_text(str(x) + " " + str(y))

        if(text == "cancel"):
            print(text)
            scan = False
            merge_img = 0
            


    def on_binary_message(self, buf):
        print(buf)
        self.send_binary(buf)


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa
        upgrade = self.headers.getheader('Upgrade')
        conn_method = self.headers.getheader('Connection')
        ws_version = self.headers.getheader('Sec-WebSocket-Version')
        ws_key = self.headers.getheader('Sec-WebSocket-Key')

        assert upgrade and (upgrade.lower() == 'websocket'), 'BAD_REQUEST U'
        assert conn_method and ('upgrade' in conn_method.lower().split(', ')), 'BAD_REQUEST C'
        assert ws_version and (13 in map(int, ws_version.split(','))), 'BAD_REQUEST V'

        handshake_key = ('%s%s' % (ws_key, MAGIC_STRING)).encode()
        accept_key = base64.encodestring(sha1(handshake_key).digest())[:-1]

        self.send_response(101, 'Switching Protocols')
        self.send_header('Upgrade', 'websocket')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Sec-WebSocket-Accept', accept_key.decode('ascii'))
        self.end_headers()

        ws = MyWebsocketHandler(self.request, "", self.server)
        ws.serve_forever()


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    httpd = ThreadingHTTPServer(("", 8081), MyHttpRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
