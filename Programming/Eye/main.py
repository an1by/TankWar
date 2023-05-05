from time import sleep
import base64

import sys
sys.path.insert(1, '../Libraries')

from tcpip import connection
connection.connect('play.aniby.net', 3030)
connection.init("camera")

import cv2
camera = cv2.VideoCapture(0)

while True:
    return_value, image = camera.read()
    cv2.imwrite('opencv.png', image)
    with open('opencv.png', mode='rb') as file:
        connection.send(
            str(base64.b64encode(file.read()))
        )
    sleep(1000)

del(camera)