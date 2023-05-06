import pygame
from pygame.locals import *
from pygame_widgets import *
from ping3 import ping, verbose_ping

def ping_server(server):
    pong = ping(server)
    return str(round(pong * 1000)) + " мс" if pong else "0 мс"

pygame.font.init()
arial_font = pygame.font.SysFont('arial', 36)

def get_text_render(text, font=arial_font, text_color = (255, 255, 255)):
    return font.render(str(text), True, text_color)

def draw_text(surface, text: pygame.Surface | str, x, y, text_color = (255, 255, 255), orientation: str="", font=arial_font):
    if not font:
        font = arial_font
    img = text if isinstance(text, pygame.Surface) else font.render(str(text), True, text_color)
    position = (x, y)
    if orientation != "":
        sw, sh = surface.get_size()
        tw, th = img.get_width(), img.get_height()
        mw, mh = 30, th * 0.08
        match orientation:
            case "up":
                position = img.get_rect(center=(sw//2 + mw + x, mh + y))
            case "down":
                position = img.get_rect(center=(sw//2 + mw + x, sh-th + mh + y))
            case "center":
                position = img.get_rect(center=(sw//2 + x, sh//2 + y))
            case "left":
                position = img.get_rect(center=(tw//2 + mw + x, sh//2 + y))
            case "right":
                position = img.get_rect(center=(sw - tw - mw + x, sh//2 + y))
    surface.blit(img, position)

def is_empty(data):
    return data == {} or data == None or data == ''

def getImage(name):
    return pygame.image.load("./resources/" + name + ".png").convert_alpha()

def getImageBox(name):
    return pygame.transform.scale(getImage(name), (cells["sub_size"], cells["sub_size"]))

cells = {
    "size": 86,
    "sub_size": 86,
    "amount": 8
}

class CoordinatesObject(object):
    def __init__(self, x = -1, y = -1):
        self.x = x
        self.y = y
        self.angle = 0
    
    def to_tuple(self):
        return (self.x, self.y)

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle
        }
    
    def from_json(self, json):
        print(json)
        self = CoordinatesObject(json["x"], json["y"])
        if "angle" in json:
            print(True)
            self.angle = json["angle"]
            print(self.angle)
        return self