
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from hashlib import sha1
from errno import EAGAIN
import SocketServer
import socket
import base64
import cv2
import pickle
import numpy as np

from websocket import WebSocketHandler, MAGIC_STRING
from scan import init,get_img
from stitch import Stitcher
from handler import ScanSocketHandler
camera = cv2.VideoCapture(0)

f = open("data/H.p","rb")
H_lst = pickle.load(f)['mtx']

f = open("data/H1.p","rb")
H1_lst = pickle.load(f)['mtx']


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

        ws = ScanSocketHandler(self.request, "", self.server, H_lst,H1_lst,"/dev/cu.wchusbserial1410",115200)
        ws.serve_forever()


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    httpd = ThreadingHTTPServer(("", 8081), MyHttpRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
