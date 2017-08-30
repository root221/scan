
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from hashlib import sha1
from errno import EAGAIN
import SocketServer
import socket
import base64
from websocket import WebSocketHandler, MAGIC_STRING

from handler import ScanSocketHandler
import cv2
import pickle
import numpy as np
import sys
import getopt

params = {}


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

        ws = ScanSocketHandler(self.request, "", self.server, params['H_lst'],params['H1_lst'],params['ser_port'],params['ser_baudrate'])
        ws.serve_forever()


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    opts,args = getopt.getopt(sys.argv[1:], "ho:x:y:p:b:", ["help", "output="])
    for opt,arg in opts:

        if opt in ("-h", "--help"):
            pass
        
        elif opt in ("-o", "--output"):    
            params['output'] = arg

        elif opt in ("-x"):
            H_lst = arg

        elif opt in ("-y"):
            H1_lst = arg

        elif opt in ("-p"):
            params['ser_port'] = arg

        elif opt in ("-b"):
            params['ser_baudrate'] = arg


    f = open("data/H.p","rb")
    H_lst = pickle.load(f)['mtx']
    params['H_lst'] = H_lst
    f = open("data/H1.p","rb")
    H1_lst = pickle.load(f)['mtx']
    params['H1_lst'] = H1_lst
    httpd = ThreadingHTTPServer(("", 8081), MyHttpRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
