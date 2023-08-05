import socketserver

storage = []

PREFIX = "#"
CMD_RETRIVE = "RETRIVE"
CMD_INSERT = "INSERT"
CMD_LENGTH = "LENGTH"
CMD_CLEAR = "CLEAR"

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global storage
        data = self.request.recv(1024).strip().decode()
        print("send from {}".format(self.client_address[0]))
        if data.startswith(PREFIX + CMD_RETRIVE):
            try:
                _, line, page = data.split(":")
                ret = storage[int(line)*int(page):int(line)*int(page)+int(line)]
                self.request.sendall("\n".join(ret).encode())
            except:
                self.request.sendall(b"0")
            return
        
        if data.startswith(PREFIX + CMD_INSERT):
            try:
                _, data = data.split(":")
                storage.append(data)
                print("\n".join(storage))
                self.request.sendall(b"1")
            except:
                self.request.sendall(b"0")
            return

        if data == PREFIX + CMD_LENGTH:
            self.request.sendall(str(len(storage)).encode())

        if data == PREFIX + CMD_CLEAR:
            storage = []
            self.request.sendall(b"1")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=9999, metavar='int', type=int)
    parser.add_argument("--bind", default="localhost")
    args = parser.parse_args()
    HOST, PORT = args.bind, args.port

    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
        print("bye.")

if __name__ == '__main__':
    main()
