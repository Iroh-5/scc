import sys

class Cipher:
    def __init__(self, key: str):
        self.key = key.encode("utf-8")

    def encrypt(self, data: bytearray) -> bytearray:
        return self.__alg__(data)

    def decrypt(self, data: bytearray) -> bytearray:
        return self.__alg__(data)

    def __alg__(self, data: bytearray) -> bytearray:
        expanded_key = (self.key * (len(data) // len(self.key) + 1))[:len(data)]

        enc_data = bytearray()
        for i in range(len(data)):
            enc_data.append(data[i] ^ expanded_key[i])

        return enc_data
