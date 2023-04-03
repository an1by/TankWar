import socket, json, time, select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("play.aniby.net", 3030)) # Подключаемся к нашему серверу. #Получаем данные из сокета.
time.sleep(3)
s.recv(2**14)
s.sendall(json.dumps({"command":"init", "who": "neck"}).encode('utf-8'))

s.setblocking(0)

# data: json
def send_data(data):
    s.sendall(bytes(json.dumps(data) ,encoding="utf-8"))

def get_data():
    received = None
    ready = select.select([s], [], [], 0.1)
    if ready[0]:
        received = s.recv(2**20)
    return (json.loads(received) if received else {})

def init():
    send_data({"command":"init", "who": "client"})

def stop():
    s.close()