import socket, json, select
import re
from utils import is_empty


class ServerConnection(object):
    def __init__(self):
        self.connected = False

    def connect(self, address, port):
        if self.connected:
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect((address, port))
        self.socket.setblocking(0)
        self.connected = True
        print(f'Connected to {address}:{port}')

    def init(self):
        self.send({"command":"init", "who": "manager"})

    def send(self, data):
        self.socket.sendall(bytes(json.dumps(data) ,encoding="utf-8"))

    def receive(self):
        to_return = []
        if self.connected:
            ready = select.select([self.socket], [], [], 0.1)
            if ready[0] and self.socket.getsockname()[1] != 0:
                received = self.socket.recv(2**20)
                if received:
                    received = received.decode('utf-8')
                    r = re.split('(\{.*?\})(?= *\{)', received)
                    to_return = [json.loads(x) for x in r if not is_empty(x)]
        return to_return

    def stop(self):
        if not self.connected:
            return
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.connected = False

connection = ServerConnection()
connection.connect('play.aniby.net', 3030)