import sys
import time
import connection

def main():
    # Set up connection
    conn = connection.Connection("localhost", int(sys.argv[1]), int(sys.argv[2]))
    conn.establish()

    # One of two processes sends message first
    if len(sys.argv) == 4 and sys.argv[3] == "start":
        conn.write('1'.encode("utf-8"))
        print("> 1")

    while True:
        # Receive number
        received_num = int(conn.read().decode("utf-8"))
        print('< {}'.format(received_num))
        time.sleep(1)
        print('> {}'.format(received_num + 1))
        # Send incremented number back
        conn.write(str(received_num + 1).encode("utf-8"))

if __name__ == "__main__":
    main()
