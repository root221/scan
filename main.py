
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
from PIL import Image
camera = cv2.VideoCapture(0)
camera.set(3,1024)
camera.set(4,768)
camera.set(5,30)
camera.set(15, -8)

global scan 
global merge_img 
global ser  

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
            global scan
            scan = True
            global merge_img
            merge_img = Image.new('RGB',(170 * 10,200 * 10),(255,255,255))
            global ser
            ser = init()
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
            offset = (170*x,200*y)
            #OpenCV stores color image in BGR format. So, the converted PIL image is also in BGR-format. The standard PIL image is stored in RGB format. 
            RGBImg =  np.zeros(img.shape,img.dtype)
            RGBImg[:,:,0] = img[:,:,2]
            RGBImg[:,:,1] = img[:,:,1]
            RGBImg[:,:,2] = img[:,:,0]
            pil_img = Image.fromarray(RGBImg)
            pil_img.save("test" + str(x) + str(y) + ".jpg") 
            crop_img = crop_image(pil_img)
            #crop_img.save("test.jpg")

            merge_img.paste(crop_img,offset)
            img_str = merge_img.tobytes("jpeg","RGB")
            merge_img.save("merge.jpg") 
            self.send_text(str(x) + " " + str(y))
            self.send_binary(img_str)

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
