
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
            merge_img = Image.new('RGB',(260 * 10,260 * 10),(255,255,255))
            for i in range(0,10):
                for j in range(0,10):
                    img = get_img(camera,i,j)
                    # convert ndarray to str
                    #img_str = cv2.imencode('.jpg', img)[1].tostring()
                    
                    # convert ndarray to PIL Image
                    offset = (130*i,130*j)
                    pil_img = Image.fromarray(img)
                    crop_img = crop_image(pil_img)

                    merge_img.paste(crop_img,offset)
                    img_str = merge_img.tobytes("jpeg","RGB")
                    self.send_text(str(i*10+j))
                    self.send_binary(img_str)
       


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
    httpd = ThreadingHTTPServer(("", 8080), MyHttpRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
