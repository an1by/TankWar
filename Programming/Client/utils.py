import pygame
import time, os
from pygame.locals import *
from pygame_widgets import *
from ping3 import ping, verbose_ping

def ping_server(server):
    pong = ping(server)
    return str(round(pong * 1000)) + " мс" if pong else "0 мс"

servers = [
    {
        "name": "Aniby.NET",
        "address": "play.aniby.net",
        "port": 3030
    },
    {
        "name": "СССР",
        "address": ""
    },
    {
        "name": "Пиндосостан",
        "address": ""
    },
    {
        "name": "КГБ",
        "address": ""
    },
    {
        "name": "ФСБ",
        "address": ""
    }
]

pygame.font.init()
font = pygame.font.SysFont('arial', 36)

def draw_text(surface, text, text_color, x, y):
    global font
    img = font.render(str(text), True, text_color)
    surface.blit(img, (x,y))

def is_empty(data):
    return data == {} or data == None or data == ''

def load_resource(name):
    return pygame.image.load(os.path.join('resources', name)).convert_alpha()

cells = {
    "size": 86,
    "sub_size": 86,
    "amount": 8
}

class CoordinatesObject(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.center = None
    
    def set_center(self, x, y):
        self.center = CoordinatesObject(x, y)
    
    def to_tuple(self):
        return (self.x, self.y)

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle
        }