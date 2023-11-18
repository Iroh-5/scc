import logging

import cipher
import connection
import utils

class Server:
    MAX_READ_BYTES = 1024

    def __init__(self):
        self.list_port = 6666
        self.conn = connection.Connection()

        self.cipher = cipher.Cipher("key")

    def process_connections(self):
        conn = self.conn
        conn.listen(self.list_port)

        conn.write(int(5555).to_bytes(2, "big"))

        self.__give_key__()

    def __recv_data__(self):
        msg = self.conn.read(Server.MAX_READ_BYTES)

        msg = self.cipher.decrypt(msg)

        return utils.unpack_data(msg)

    def __give_key__(self):
        print(self.__recv_data__())

if __name__ == '__main__':
    server = Server()
    server.process_connections()
