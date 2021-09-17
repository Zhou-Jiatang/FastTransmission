import os
from sys import argv

from qrcode import make

from handler.simple_http_handler import SimpleHTTPRequestHandler
from server.simple_http_server import SimpleHTTPServer
from utils.util import get_IP


dir_path = argv[1]
HOST, PORT = get_IP(), 8888
path = "http://" + HOST + ":" + str(PORT) + "/index.html"
print(path)
img = make(data=path)
img.show()
SimpleHTTPServer((HOST, PORT), SimpleHTTPRequestHandler, dir_path).start_serve()
