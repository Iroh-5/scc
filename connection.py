import socket
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

class EstablishedConnection:
    def __init__(self, sock):
        self.sock = sock

    def write(self, data: bytes) -> None:
        self.sock.sendall(data)

    def read(self, bytes_num: int) -> bytes:
        return self.sock.recv(bytes_num)

# Class represents one directional connection
# NOTE: Either connect or listen must be called. Not both!
class Connection(EstablishedConnection):
    def __init__(self):
        super().__init__(socket.socket)

    def connect(self, port: int) -> None:
        logging.debug(f"Connecting to port {port}")
        while True:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect(('localhost', port))
            except OSError:
                self.sock.close()
                continue

            break
        logging.debug(f"Connection to port {port} established")

    def listen(self, port: int):
        self.__init_listener__(port)

        self.lsock.listen(1)
        logging.debug(f"Waiting conneciton on port {port}")

        sock, _ = self.lsock.accept()
        logging.debug(f"Connection to port {port} accepted")

        return EstablishedConnection(sock)

    def __init_listener__(self, port):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.bind(('localhost', port))

        Connection.__init_listener__.__code__ = (lambda self, port:None).__code__
