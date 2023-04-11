import pygame
from utils import CoordinatesObject, load_resource
tank_list = []

def setList(new_list, margin, cell_size):
    global tank_list
    tank_list = []
    for tank in new_list:
        newt = Tank(tank["team"], tank["number"], tank["dead"])
        newt.move(CoordinatesObject(
            margin.x + tank["position"]["x"] * cell_size, 
            margin.y + tank["position"]["y"] * cell_size
        ))

tank_image = load_resource('tank.png')

def getByNumber(team, number):
    for tank in tank_list:
        if tank.number == number and tank.team == team:
            return tank
    return None

class Tank(object):
    def __init__(self, team, number, dead):
        self.team = team,
        self.number = number,
        # self.position.angle = position["angle"]
        self.dead = dead
        self.image = tank_image
        self.image = pygame.transform.scale(self.image, (72, 72)) 
        tank_list.append(self)
    
    def move(self, position):
        self.rect.x = position.x
        self.rect.y = position.y
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))