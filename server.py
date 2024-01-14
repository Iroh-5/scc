import logging
import threading

import cipher
import connection
import utils

class Server:
    clients = {}

    def __init__(self):
        self.list_port = 6666
        self.conn = connection.Connection()

    def process_connections(self):
        logging.info("Starting...")

        while True:
            new_conn = self.conn.listen(self.list_port)
            self.clients[""] = (new_conn, cipher.Cipher(""), 0)

            client_name, client_port = self.__recv_data__("")
            self.clients[client_name] = (new_conn, cipher.Cipher(self.__get_client_key__(client_name)), client_port)

            threading.Thread(target=Server.__process_client__, args=(self, client_name), daemon=True).start()

    def __process_client__(self, client_name):
        while True:
            command = self.__recv_data__(client_name)[0]
            command = ' '.join(command.split())

            if command == "get users":
                self.__give_users__(client_name)
            elif ' '.join(command.split()[:2]) == "get key":
                self.__give_key__((client_name, command.split()[2]))
            elif ' '.join(command.split()[:2]) == "get port":
                self.__give_port__(client_name, command.split()[2])
            else:
                logging.error(f"Got unknown command {command}")

    def __give_port__(self, cname, other_cname):
        port = self.clients[other_cname][2]
        self.__send_data__(cname, port)

    def __give_key__(self, clients_names):
        lclient, rclient = clients_names

        key = lclient + "to" + rclient + "key"

        lname, rname, Nl = self.__recv_data__(lclient)

        first_part  = self.clients[lclient][1].encrypt((str(Nl) + '|' + rclient + '|'  + key).encode("utf-8")).decode("utf-8")
        second_part = self.clients[rclient][1].encrypt((key + '|' + lclient).encode("utf-8")).decode("utf-8")
        second_part = self.clients[lclient][1].encrypt((second_part).encode("utf-8")).decode("utf-8")
        self.__send_data__(lclient, first_part, second_part)

    def __give_users__(self, cname):
        self.__send_data__(cname, *list(self.clients.keys()))

    def __send_data__(self, cname, *data):
        conn, cipher, _ = self.clients[cname]
        utils.send_data(conn, *data)

    def __recv_data__(self, cname):
        conn, cipher, _ = self.clients[cname]
        return utils.recv_data(conn)

    def __get_client_key__(self, client_name):
        key = client_name
        for c in reversed(client_name):
            key += c

        return key

if __name__ == '__main__':
    server = Server()
    server.process_connections()
