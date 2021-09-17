class BaseRequestHandler:
    def __init__(self, server, request, client_address):
        self.server = server
        self.request = request
        self.client_address = client_address

    def handle(self):
        pass


class StreamRequestHandler(BaseRequestHandler):

    def __init__(self, server, request, client_address):
        BaseRequestHandler.__init__(self, server, request, client_address)
        self.rfile = self.request.makefile('rb')
        self.wfile = self.request.makefile('wb')
        self.wbuf = []

    def encode(self, msg):
        if not isinstance(msg, bytes):
            msg = bytes(msg, encoding="utf-8")
        return msg

    def decode(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode()
        return msg

    def read(self, length):
        msg = self.rfile.read(length)
        return self.decode(msg)

    def read_byte(self, length):
        return self.rfile.read(length)

    def readline(self, length=65536):
        msg = self.rfile.readline(length).strip()
        return self.decode(msg)

    def write_content(self, msg):
        msg = self.encode(msg)
        self.wbuf.append(msg)

    def send(self):
        for line in self.wbuf:
            self.wfile.write(line)
        self.wfile.flush()
        self.wbuf = []

    def close(self):
        self.wfile.close()
        self.rfile.close()
