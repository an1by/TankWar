import pygame
from utils import CoordinatesObject, cells
tank_list = []

def setList(new_list):
    global tank_list
    tank_list = []
    for tank in new_list:
        newt = Tank(tank["team"], tank["number"], tank["dead"])
        coords = CoordinatesObject(
            tank["position"]["x"], 
            tank["position"]["y"]
        )
        newt.move(coords)
# {'action': 'set_tanks', 'tanks': [{'team': 'red', 'number': 1, 'position': {'x': 2, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 2, 'position': {'x': 3, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 3, 'position': {'x': 4, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 4, 'position': {'x': 5, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 5, 'position': {'x': 6, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 6, 'position': {'x': 7, 'y': 0, 'angle': 0}, 'dead': False}]}

t90_image = pygame.image.load("./resources/tanks/t-90.png").convert_alpha()
abrams_image = pygame.image.load("./resources/tanks/abrams.png").convert_alpha()

def getByNumber(team, number):
    for tank in tank_list:
        if tank.number == number and tank.team == team:
            return tank
    return None

active_tank = None #

def foundTank(position):
    for tank in tank_list:
        if tank.position.x == position.x and tank.position.y == position.y:
            return tank
    return None

step_show_surface = pygame.Surface((cells["size"] * 3, cells["size"] * 3))  # the size of your rect
step_show_surface.set_alpha(128)                # alpha level
step_show_surface.fill((255, 0, 0))           # this fills the entire surface

class Tank(object):
    def __init__(self, team, number, dead):
        self.team = team
        self.number = number
        self.dead = dead
        self.image = (t90_image if team == "red" else abrams_image)
        self.image = pygame.transform.scale(self.image, (72, 72)) 
        self.position = CoordinatesObject(0, 0)
        tank_list.append(self)
    
    def move(self, position):
        self.position.x = position.x
        self.position.y = position.y

    def draw(self, surface):
        if active_tank and active_tank.number == self.number:
            surface.blit(step_show_surface, ((self.position.x - 1)  * cells["size"], (self.position.y - 1) * cells["size"]))
        surface.blit(self.image, (self.position.x  * cells["size"], self.position.y * cells["size"]))