import socket, pickle
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.0.178", 3030)) # Подключаемся к нашему серверу. #Получаем данные из сокета.

# returns: json
def get_data():
        s.sendall(json.dumps({"command":"get"}).encode('utf-8'))
        data = s.recv(1024)
        return json.loads(data.decode("utf-8"))

# data: json
def send_data(data):
        s.sendall(bytes(json.dumps(data) ,encoding="utf-8"))

def stop():
        s.close()
