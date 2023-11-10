import socket
import logging
import concurrent.futures

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

class Connection:
    def __init__(self, host: str, lport: int, wport: int):
        self.host = host

        self.listening_port = lport
        self.writing_port   = wport

        self.lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsocket.bind((self.host, self.listening_port))

        self.MAX_READ_BYTES = 1024

    def establish(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            def create_reading_conn(sock):
                sock.listen(1)
                logging.debug(f"Waiting conneciton on port {self.listening_port}")
                return sock.accept()

            rconn_future = executor.submit(create_reading_conn, self.lsocket)

            logging.debug(f"Connecting to port {self.writing_port}")
            while True:
                self.wsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.wsocket.connect((self.host, self.writing_port))
                except OSError:
                    self.wsocket.close()
                    continue

                break

            logging.debug(f"Connection to port {self.writing_port} established")

            rsock, _ = rconn_future.result()
            self.rsocket = rsock

            logging.info("Connection established")

            self.lsocket.close()

    def write(self, data: bytes) -> None:
        self.wsocket.sendall(data)

    def read(self) -> bytes:
        return self.rsocket.recv(self.MAX_READ_BYTES)
