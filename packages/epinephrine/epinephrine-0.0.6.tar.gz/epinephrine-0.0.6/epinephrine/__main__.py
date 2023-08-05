import socketserver
from . import *


class Storage():
    def __init__(self, storage=[], sendall=None):
        self.storage = storage
        self.sendall = sendall

    def handle(self, signal):
        command_list = [
            (CMD_RETRIVE, self.command_retrive),
            (CMD_INSERT, self.command_insert),
            (CMD_LENGTH, self.command_length),
            (CMD_CLEAR, self.command_clear),
            (CMD_DUMP, self.command_dump),
        ]

        for command_str, func in command_list:
            if signal.startswith(PREFIX + command_str):
                return func(signal[1:])

    def command_retrive(self, data):
        try:
            _, line, page = data.split(":")
            count = int(line) * int(page)
            count = count if count >= 0 else 0
            ret = self.storage[count:count + int(line)]
            self.sendall("\n".join(ret).encode())
        except:
            self.sendall(SIG_FAIL)

    def command_insert(self, data):
        try:
            _, data = data.split(":")
            self.storage.append(data)
            self.sendall(SIG_OK)
        except:
            self.sendall(SIG_FAIL)

    def command_length(self, data):
        self.sendall(str(len(self.storage)).encode())

    def command_clear(self, data):
        self.storage = []
        self.sendall(SIG_OK)

    def command_dump(self, data):
        import pickle
        import os
        import sys
        pickle.dump(self.storage, open(os.path.join(os.getcwd(), "dump.epdb"), "wb"))
        self.sendall(SIG_OK)



class Handler(socketserver.BaseRequestHandler):

    import functools
    @functools.lru_cache()
    def get_storage(self):
        return Storage(sendall=self.request.sendall)

    def handle(self):
        data = self.request.recv(1024).strip().decode()
        print("send from {}".format(self.client_address[0]))
        return self.get_storage().handle(data)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=9999, metavar='int', type=int)
    parser.add_argument("--bind", default="localhost")
    args = parser.parse_args()
    HOST, PORT = args.bind, args.port

    server = socketserver.TCPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
        print("bye.")

if __name__ == '__main__':
    main()
