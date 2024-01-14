import struct
import time

MAX_READ_BYTES = 1024

def pack_data(*data) -> bytes:
    """Packes data into binary format

    Function takes arbitrary number of arguments of arbitrary types
    and serializes them into contigues bytes array
    """

    msg_fmt = '!'
    header_fmt = '!'

    strs_lens = list()
    data_list = list(data)

    for i in range(len(data_list)):
        if type(data_list[i]).__name__ == 'str':
            str_len = len(data_list[i])

            strs_lens.append(str_len)

            msg_fmt    += ' {}s'.format(str_len)
            header_fmt += ' I'

            data_list[i] = data_list[i].encode('utf-8')
        elif type(data_list[i]).__name__ == 'int':
            msg_fmt += ' I'
        else:
            raise Exception('Unsupported type provided {}'.format(type(data_list[i]).__name__))

    packed_fmt  = struct.Struct('!l {}s'.format(len(msg_fmt))).pack(len(msg_fmt), msg_fmt.encode('utf-8'))
    packed_data = struct.Struct(msg_fmt).pack(*data_list)

    # [size of format][format][binary data]
    return bytes(bytearray(packed_fmt) + bytearray(packed_data))

def unpack_data(data: bytes) -> list:
    """Unpackes data represented in binary format

    Function takes a bytes array and decomposes it into
    a list of values which were encoded into that array
    """

    fmt_size = struct.Struct('!l').unpack(data[:4])[0]
    fmt      = struct.Struct('!{}s'.format(fmt_size)).unpack(data[4:4 + fmt_size])[0]
    items    = struct.Struct(fmt).unpack(data[4 + fmt_size:])

    items_list = list(items)
    for i in range(len(items_list)):
        if type(items_list[i]).__name__ == 'bytes':
            items_list[i] = items_list[i].decode('utf-8')

    return items_list

def send_data_enc(cipher, conn, *data):
    time.sleep(0.5)

    msg = pack_data(*data)

    msg = cipher.encrypt(msg)

    conn.write(msg)

def recv_data_enc(cipher, conn):
    msg = conn.read(MAX_READ_BYTES)

    msg = cipher.decrypt(msg)

    return unpack_data(msg)

def send_data(conn, *data):
    time.sleep(0.5)

    msg = pack_data(*data)

    conn.write(msg)

def recv_data(conn):
    msg = conn.read(MAX_READ_BYTES)

    return unpack_data(msg)
