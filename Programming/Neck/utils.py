import os, pygame
rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

cells = {
    "size": 64,
    "amount": 8
}

def getImage(name):
    image = pygame.image.load("./resources/" + name + ".png").convert_alpha()
    return pygame.transform.scale(image, (cells["size"], cells["size"]))

def is_empty(data):
    return data == {} or data == None or data == ''

class CoordinatesObject(object):
    def __init__(self, x = -1, y = -1):
        self.x = x
        self.y = y
        self.angle: float = 0.0
    
    def to_tuple(self):
        return (self.x, self.y)

    def to_json(self):
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle
        }
    
    def from_json(self, json):
        self = CoordinatesObject(json["x"], json["y"])
        if "angle" in json:
            self.angle = json["angle"]
        return self