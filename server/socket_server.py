import socket
import threading


class TCPServer:

    def __init__(self, server_address, handler_class, dir_path):
        self.server_address = server_address
        self.HandlerClass = handler_class
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_shutdown = False
        self.dir_path = dir_path

    def start_serve(self):
        self.socket.bind(self.server_address)
        self.socket.listen(10)
        while not self.is_shutdown:
            request, client_address = self.get_request()
            try:
                self.process_request_multithread(request, client_address)
            except Exception as e:
                print(e)


    def get_request(self):
        return self.socket.accept()

    def process_request(self, request, client_address):
        handler = self.HandlerClass(self, request, client_address, self.dir_path)
        handler.handle()
        self.close_request(request)

    def process_request_multithread(self, request, client_address):
        t = threading.Thread(target=self.process_request,
                             args=(request, client_address))
        t.start()


    def close_request(self, request):
        request.shutdown(socket.SHUT_WR)
        request.close()

    def shutdown(self):
        self.is_shutdown = True



