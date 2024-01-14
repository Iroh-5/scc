import logging
import random
import threading

import cipher
import connection
import utils

class Client:
    def __init__(self, name: str, lst_port: int):
        self.lst_port = lst_port
        self.server_list_port = 6666
        self.server_conn = connection.Connection()

        self.name = name

        self.cipher = cipher.Cipher(self.__generate_key__())

        self.__connect_to_server__(lst_port)

    def get_online_users(self):
        self.__send_data_serv__("get users")
        return self.__recv_data_serv__()

    def initiate_connection_to_user(self, other_name):
        logging.info("Starting key exchanging process..")

        self.other_name = other_name

        self.__connect_to_user__()
        self.__get_key__()
        self.__start_reading_thread__()

    def start_listening(self):
        logging.info("Starting waiting for other clients ot connect...")

        self.other_conn = connection.Connection()
        self.other_conn = self.other_conn.listen(self.lst_port)

        self.__wait_for_key__()
        self.__start_reading_thread__()

    def send_message(self, message):
        self.__send_data_cli__(message, encrypt=True)

    def __connect_to_user__(self):
        self.__send_data_serv__(f"get port {self.other_name}")

        port = self.__recv_data_serv__()[0]

        self.other_conn = connection.Connection()
        self.other_conn.connect(port)

    def __wait_for_key__(self):
        data = self.__recv_data_cli__()[0]

        data = self.cipher.decrypt(data.encode("utf-8")).decode("utf-8")

        sep_ind = data.find('|')
        key = data[:sep_ind]
        self.other_name = data[sep_ind + 1:]

        self.cipher = cipher.Cipher(key)

        N = random.randint(0, 2 ** 32 - 1)
        self.__send_data_cli__(N, encrypt=True)

        N_mod = self.__recv_data_cli__(decrypt=True)[0]

        if N_mod != N - 1:
            raise Exception("Got wrong modified N")

        logging.info(f"Secure connection to {self.other_name} has been established. Key: {key}")

    def __start_reading_thread__(self):
        threading.Thread(target=Client.__read_messages_from_client__, args=(self,), daemon=True).start()

    def __read_messages_from_client__(self):
        while True:
            print("[{}] {}".format(self.other_name, self.__recv_data_cli__(decrypt=True)[0]))

    def __get_key__(self):
        self.__send_data_serv__(f"get key {self.other_name}")

        N = random.randint(0, 2 ** 32 - 1)

        self.__send_data_serv__(self.name, self.other_name, N)

        first_part, second_part = self.__recv_data_serv__()
        first_part  = self.cipher.decrypt(first_part.encode("utf-8")).decode("utf-8")
        second_part = self.cipher.decrypt(second_part.encode("utf-8")).decode("utf-8")

        first_sep = first_part.find('|')
        N_got = int(first_part[:first_sep])
        if N_got != N:
            raise Exception(f"Bad secret numbers. Expected {N}, got {Ng}")

        first_part = first_part[first_sep + 1:]
        other_name_got = first_part[:first_part.find('|')]
        key = first_part[first_part.find('|') + 1:]
        self.cipher = cipher.Cipher(key)

        if other_name_got != self.other_name:
            raise Exception("Names are not equal")

        self.__send_data_cli__(second_part)

        N_other = self.__recv_data_cli__(decrypt=True)[0]
        self.__send_data_cli__(N_other - 1, encrypt=True)

        logging.info(f"Secure connection to {self.other_name} has been established. Key: {key}")

    def __connect_to_server__(self, lst_port):
        conn = self.server_conn
        conn.connect(self.server_list_port)
        self.__send_data_serv__(self.name, lst_port)

        logging.info("Successfully connected to server")

    def __send_data_serv__(self, *data):
        utils.send_data(self.server_conn, *data)

    def __recv_data_serv__(self):
        return utils.recv_data(self.server_conn)

    def __send_data_cli__(self, *data, encrypt=False):
        if encrypt:
            utils.send_data_enc(self.cipher, self.other_conn, *data)
        else:
            utils.send_data(self.other_conn, *data)

    def __recv_data_cli__(self, decrypt=False):
        if decrypt:
            return utils.recv_data_enc(self.cipher, self.other_conn)
        else:
            return utils.recv_data(self.other_conn)

    def __generate_key__(self):
        key = self.name
        for c in reversed(self.name):
            key += c

        return key

if __name__ == "__main__":
    logging.info("Starting...")

    client_data = input("Enter your name and listening port\n$ ")
    client_name, client_port = client_data.split()

    client = Client(client_name, int(client_port))

    print("You can see online users by typing 'show users'")
    print("You can start communicating with user by typing 'chat *username*'")
    print("Or you can start waiting for other clients to text you by typing 'listen'")

    state = 'IDLE'
    prompt = '$ '

    while True:
        user_input = input(prompt)

        if state == 'MESSAGING':
            client.send_message(user_input)
            continue

        command = ' '.join(user_input.split())

        if command == "show users":
            print(client.get_online_users())
        elif command.split()[0] == "chat":
            client.initiate_connection_to_user(command.split()[1])
            state = 'MESSAGING'
            prompt = ''
        elif command == "listen":
            client.start_listening()
            state = 'MESSAGING'
            prompt = ''
        else:
            print("Wrong command")
