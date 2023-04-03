import pygame
import time
from pygame.locals import *
from pygame_widgets import *
from ping3 import ping, verbose_ping

def ping_server(server):
    pong = ping(server)
    return str(round(pong * 1000)) + " мс" if pong else "0 мс"

servers = [
    {
        "name": "Aniby.NET",
        "address": "play.aniby.net"
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