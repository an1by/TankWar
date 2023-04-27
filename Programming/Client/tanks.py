import pygame
from utils import CoordinatesObject, cells, getImage
import tcpip, obstacles
tank_list = []

def setList(new_list):
    global tank_list
    tank_list = []
    for tank in new_list:
        print(tank)
        newt = Tank(tank["team"], tank["number"], tank["dead"])
        newt.set_position(CoordinatesObject().from_json(tank["position"]))
# {'action': 'set_tanks', 'tanks': [{'team': 'red', 'number': 1, 'position': {'x': 2, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 2, 'position': {'x': 3, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'red', 'number': 3, 'position': {'x': 4, 'y': 7, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 4, 'position': {'x': 5, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 5, 'position': {'x': 6, 'y': 0, 'angle': 0}, 'dead': False}, {'team': 'blue', 'number': 6, 'position': {'x': 7, 'y': 0, 'angle': 0}, 'dead': False}]}

t90_image = getImage('tanks/t-90')
abrams_image = getImage('tanks/abrams')
t90_dead_image = getImage('tanks/t-90_dead')
abrams_dead_image = getImage('tanks/abrams_dead')

def getByNumber(team, number):
    for tank in tank_list:
        if tank.number == number and tank.team == team:
            return tank
    return None

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
        """
        Инициализация танков
        """
        self.team = team
        self.number = number
        self.dead = dead

        self.original_image = pygame.transform.scale((t90_image if team == "red" else abrams_image), (72, 72))
        self.image = self.original_image

        self.position = CoordinatesObject(0, 0)
        # self.position.angle = number * 90
        # self.rotate(self.position.angle)

        tank_list.append(self)
    
    def kill(self):
        """
        Функция для инициализации убийства танка
        """
        self.dead = True
        self.original_image = pygame.transform.scale((t90_dead_image if self.team == "red" else abrams_dead_image), (72, 72))
        self.image = self.original_image
        self.rotate(self.position.angle)

    def move_and_send(self, position):
        """
        Функция для передвижения танка и инициализации этого передвижения на сервере
        """
        if self.move(position):
            tcpip.send_data({
                "command": "step",
                "what": "move",
                "number": self.number,
                "position": position.to_json()
            })
            return True
        return False

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.original_image, angle - 90)

    def set_position(self, position):
        self.position.x, self.position.y = position.x, position.y
        if position.angle:
            self.position.angle = position.angle
            self.rotate(position.angle)

    def move(self, position):
        if self.can_move(position):
            self.set_position(position)
            return True
        return False

    def can_move(self, position):
        if self.dead:
            return False
        moving = abs(self.position.x - position.x) + abs(self.position.y - position.y)
        if moving == 1:
            if obstacles.raycastTrajectory(self.position, position) != []:
                return False
            for tank in tank_list:
                if tank.position.x == position.x and tank.position.y == position.y:
                    return False
            return True
        return False
    
    def get_ranges(self):
        match self.position.angle:
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
            case 90: # 90 - вверх
                return [
                    range(-1, 2),
                    range(-3, 0)
                ]
            case _:
                return [
                    range(1, 4),
                    range(-1, 2)
                ]

    def raycast(self, position):
        arr = []
        rx = abs(self.position.x - position.x)
        ry = abs(self.position.y - position.y)
        k = ry / rx if rx != 0 else 0
        for x in range(self.position.x, position.x + 1):
            y = k * x
            tank = foundTank(CoordinatesObject(x, y))
            if tank != None and tank != self:
                arr.append(tank)
        return arr

    def can_fire(self, position):
        if self.dead:
            return False
        ranges = self.get_ranges()
        for x in ranges[0]:
            for y in ranges[1]:
                new_position = CoordinatesObject(
                    self.position.x + x,
                    self.position.y + y
                )
                if new_position.x == position.x and new_position.y == position.y:
                    for obstacle in obstacles.raycastTrajectory(
                        self.position,
                        new_position
                    ):
                        if obstacle.type == "full":
                            return False
                    found = foundTank(new_position)
                    if found and (found.team == self.team or found.dead):
                        return False
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
        if active_tank and active_tank.number == self.number and active_tank.team == self.team and not self.dead:
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
                            if self.can_fire(new_pos):
                                surface.blit(fire_surface, 
                                    (new_pos.x  * cells["size"], new_pos.y * cells["size"])
                                )
        surface.blit(self.image, (self.position.x  * cells["size"], self.position.y * cells["size"]))

"""
Активный выбранный танк
"""
active_tank: Tank = None