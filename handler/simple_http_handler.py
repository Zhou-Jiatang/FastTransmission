import base64
import json
import math
import os
import sys
from threading import Lock
from urllib import parse


import psutil

from handler.base_http_handler import BaseHTTPRequestHandler
from utils.util import get_free_space

# RESOURCES_PATH = os.path.join(os.path.abspath(os.path.dirname(__name__)), '../resources')
# RESOURCES_PATH = '../resources/'
RESOURCES_PATH = os.path.join(os.path.dirname(sys.argv[0]), './resources/')


mem = psutil.virtual_memory()
except_num = {}
get_num = {}
lock = Lock()
tmp_prefix = "tmp_"
MB_to_Bytes = 1024 * 1024


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, server, request, client_address, dir_path):
        BaseHTTPRequestHandler.__init__(self, server, request, client_address, dir_path)
        self.routing = {
            "/check_disk": self.check_disk,
            "/": self.POST_FILE
        }

    def get_relative_path(self, path):
        url_result = parse.urlparse(path)
        relative_path = str(url_result[2])
        return relative_path

    def get_method(self, path):
        return self.routing[path]

    def get_resources(self, path):
        resource_path = self.get_relative_path(path)
        if resource_path.startswith('/'):
            resource_path = resource_path[1:]
        resource_path = os.path.join(RESOURCES_PATH, resource_path)
        if os.path.exists(resource_path) and os.path.isfile(resource_path):
            return True, resource_path
        else:
            return False, resource_path

    def do_GET(self):
        found, resource_path = self.get_resources(self.path)
        if not found:
            self.write_error(404)
            self.send()
        else:
            with open(resource_path, 'rb') as f:
                fs = os.fstat(f.fileno())
                clength = str(fs[6])
                self.write_response(200)
                self.write_header('Content-Length', clength)
                self.write_header('Access-Control-Allow-Origin', 'http://%s:%d' %
                                  (self.server.server_address[0], self.server.server_address[1]))
                self.end_headers()
                while True:
                    buf = f.read(2048)
                    if not buf:
                        break
                    self.write_content(buf)

    def check_disk(self):
        body = json.loads(self.body)
        file_name = body['file_name']
        file_size = body['file_size']
        space_in_MB = get_free_space(self.disk_path)
        sliceSize_in_Byte = min(float(mem.free) / 16, 100*MB_to_Bytes)

        enoughSpace = space_in_MB - min(file_size, sliceSize_in_Byte*1.5/MB_to_Bytes) >= (file_size / MB_to_Bytes)
        if enoughSpace:
            except_num[file_name] = math.ceil(file_size / sliceSize_in_Byte)
            get_num[file_name] = 0
        response = {
            'message': 'success',
            'code': 0,
            'enoughSpace': enoughSpace,
            'sliceSize': sliceSize_in_Byte if enoughSpace else -1,
            'sliceNum': except_num[file_name] if enoughSpace else -1
        }
        response = json.dumps(response)
        self.write_response(200)
        self.write_header('Content-Length', len(response))
        self.write_header('Access-Control-Allow-Origin', 'http://%s:%d' %
                          (self.server.server_address[0], self.server.server_address[1]))
        self.end_headers()
        self.write_content(response)

    def POST_FILE(self):
        data = self.body
        name = base64.b64decode(self.headers['filename']).decode()
        tmp_file_name = os.path.join(self.disk_path, tmp_prefix + name + self.headers['index'])
        with open(tmp_file_name, 'wb+') as f:
            f.write(data)
            f.flush()

            lock.acquire()
            if name not in get_num.keys():
                lock.release()
                print("error: get_num doesn't have key.", name)
                return
            get_num[name] = get_num[name] + 1
            diff = get_num[name] - except_num[name]
            lock.release()

        if diff == 0:
            self.merge_file(name)

        response = {'message': 'success', 'code': 0}
        response = json.dumps(response)
        self.write_response(200)
        self.write_header('Content-Length', len(response))
        self.write_header('Access-Control-Allow-Origin', 'http://%s:%d' %
                          (self.server.server_address[0], self.server.server_address[1]))
        self.end_headers()
        self.write_content(response)

    def merge_file(self, name):
        num = except_num[name]
        filename = os.path.join(self.disk_path, name)
        if num == 1:
            os.rename(os.path.join(self.disk_path, tmp_prefix + name + str(0)), filename)
        else:
            with open(filename, 'wb+') as file:
                for i in range(num):
                    tmp_filename = os.path.join(self.disk_path, tmp_prefix + name + str(i))
                    with open(tmp_filename, 'rb') as tmp_file:
                        file.write(tmp_file.read())
                    os.remove(tmp_filename)
        print("finish merging")
        except_num.pop(name)
        get_num.pop(name)



