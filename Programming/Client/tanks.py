import pygame
from utils import CoordinatesObject, cells, getImage
import tcpip
tank_list = []

def setList(new_list):
    global tank_list
    tank_list = []
    for tank in new_list:
        print(tank)
        newt = Tank(tank["team"], tank["number"], tank["dead"])
        newt.position.x = tank["position"]["x"]
        newt.position.y = tank["position"]["y"]
# {'action': 'set_tanks', 'tanks': [{'team': 'red', 'number': 1, 'position': {'x': 2, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 2, 'position': {'x': 3, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 3, 'position': {'x': 4, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 4, 'position': {'x': 5, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 5, 'position': {'x': 6, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 6, 'position': {'x': 7, 'y': 0, 'angle': 0}, 'dead': False}]}

t90_image = getImage('tanks/t-90')
abrams_image = getImage('tanks/abrams')

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

step_surface = pygame.Surface((cells["size"], cells["size"]))
step_surface.set_alpha(128)
step_surface.fill((0, 0, 200))

fire_surface = pygame.Surface((cells["size"], cells["size"]))
fire_surface.set_alpha(128)
fire_surface.fill((255, 0, 0))

class Tank(object):
    def __init__(self, team, number, dead):
        self.team = team
        self.number = number
        self.dead = dead
        self.image = (t90_image if team == "red" else abrams_image)
        self.image = pygame.transform.scale(self.image, (72, 72)) 
        self.position = CoordinatesObject(0, 0)
        self.position.angle = 90
        tank_list.append(self)
    
    def move_and_send(self, position):
        if self.move(position):
            tcpip.send_data({
                "command": "step",
                "what": "move",
                "number": self.number,
                "position": position.to_json()
            })
            return True
        return False

    def move(self, position):
        if self.can_move(position):
            self.position.x, self.position.y = position.x, position.y
            if position.angle:
                self.position.angle = position.angle
            return True
        return False

    def can_move(self, position):
        moving = abs(self.position.x - position.x) + abs(self.position.y - position.y)
        if moving == 1:
            for tank in tank_list:
                if tank.position.x == position.x and tank.position.y == position.y:
                    return False
            return True
        return False
    
    def get_ranges(self):
        match self.position.angle:
            case 0:
                return [
                    range(1, 4),
                    range(-1, 2)
                ]
            case 180:
                return [
                    range(-3, 0),
                    range(-1, 2)
                ]
            case 270:
                return [
                    range(-1, 2),
                    range(1, 4)
                ]
            case _: # 90 - вверх
                return [
                    range(-1, 2),
                    range(-3, 0)
                ]

    def can_fire(self, position):
        ranges = self.get_ranges()
        for x in ranges[0]:
            for y in ranges[1]:
                if self.position.x + x == position.x and self.position.y + y == position.y:
                    return True
        return False

    def fire_and_send(self, position):
        if self.can_fire(position):
            tcpip.send_data({
                "command": "step",
                "what": "fire",
                "number": self.number,
                "position": position.to_json()
            })
            return True
        return False

    def draw(self, surface, current_choose):
        if active_tank and active_tank.number == self.number and active_tank.team == self.team:
            match (current_choose):
                case "move":
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            new_pos = CoordinatesObject(
                                self.position.x + x,
                                self.position.y + y
                            )
                            if abs(x) != abs(y) and self.can_move(new_pos):
                                surface.blit(step_surface, 
                                    (new_pos.x  * cells["size"], new_pos.y * cells["size"])
                                )
                case "fire":
                    ranges = self.get_ranges()
                    for x in ranges[0]:
                        for y in ranges[1]:
                            new_pos = CoordinatesObject(
                                self.position.x + x,
                                self.position.y + y
                            )
                            surface.blit(fire_surface, 
                                (new_pos.x  * cells["size"], new_pos.y * cells["size"])
                            )
        surface.blit(self.image, (self.position.x  * cells["size"], self.position.y * cells["size"]))