import socket, json, time, select
import re
from utils import is_empty

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# data: json
def send_data(data):
    s.sendall(bytes(json.dumps(data) ,encoding="utf-8"))

def get_data():
    to_return = []
    ready = select.select([s], [], [], 0.1)
    if ready[0] and s.getsockname()[1] != 0:
        received = s.recv(2**20)
        if received:
            received = received.decode('utf-8')
            r = re.split('(\{.*?\})(?= *\{)', received)
            to_return = [json.loads(x) for x in r if not is_empty(x)]
    return to_return

def connect(address, port):
    s.connect((address, port))
    print(f'Connected to {address}:{port}')
    s.setblocking(0)

def connect_default():
    connect('play.aniby.net', 3030)

def init():
    send_data({"command":"init", "who": "client"})

def stop():
    s.close()