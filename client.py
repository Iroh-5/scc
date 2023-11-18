import sys
import time
import logging
import random

import cipher
import connection
import utils

class Client:
    def __init__(self, name: str):
        self.server_list_port = 6666
        self.server_conn = connection.Connection()

        self.name = name

        self.cipher = cipher.Cipher("key")

    def initiate_connection(self, other_name: str):
        self.__connect_to_server__()
        self.__get_key__(other_name)

    def __connect_to_server__(self):
        conn = self.server_conn
        conn.connect(self.server_list_port)

    def __send_data__(self, *data):
        msg = utils.pack_data(*data)

        msg = self.cipher.encrypt(msg)

        self.server_conn.write(msg)

    def __get_key__(self, other_name: str):
        # First step
        # Alice sends (A,B,Na)
        number = random.randrange(2 ** 32 - 1)
        self.__send_data__(self.name, other_name, number)

if __name__ == "__main__":
    client = Client("Alice")
    client.initiate_connection("Bob")

