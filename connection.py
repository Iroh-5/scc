import socket
import logging

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# Class represents one directional connection
# NOTE: Either connect or listen must be called. Not both!
class Connection:
    def connect(self, port: int) -> None:
        logging.debug(f"Connecting to port {port}")
        while True:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.connect(('localhost', port))
            except OSError:
                self.socket.close()
                continue

            break
        logging.info(f"Connection to port {port} established")

    def listen(self, port: int) -> None:
        lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsocket.bind(('localhost', port))

        lsocket.listen(1)
        logging.debug(f"Waiting conneciton on port {port}")

        sock, _ = lsocket.accept()
        logging.debug(f"Connection to port {port} accepted")

        self.socket = sock

    def write(self, data: bytes) -> None:
        self.socket.sendall(data)

    def read(self, bytes_num: int) -> bytes:
        return self.socket.recv(bytes_num)
