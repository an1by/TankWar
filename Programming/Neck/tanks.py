# Инициализация папки общих библиотек
import sys
sys.path.insert(1, '../Libraries')

import pygame
from utils import *
from tcpip import connection

green_tank = {
    "alive": getImage('tanks/green'),
    "dead": getImage('tanks/green_dead')
}

yellow_tank = {
    "alive": getImage('tanks/yellow'),
    "dead": getImage('tanks/yellow_dead')
}

step_surface = pygame.Surface((cells["size"], cells["size"]))
step_surface.set_alpha(128)
step_surface.fill((0, 0, 200))

fire_surface = pygame.Surface((cells["size"], cells["size"]))
fire_surface.set_alpha(128)
fire_surface.fill((255, 0, 0))

class Tank(object):
    """
    Класс танка
    """
    def __init__(self, team: str, number: int = None, dead = False):
        """
        Инициализация танков
        """
        self.team = team
        if number:
            self.number = number
        else:
            count = 0
            for t in tank_list:
                if t.team == team:
                    count += 1
            self.number = count
        self.dead = dead

        self.original_image =  (green_tank if team == "red" else yellow_tank)["alive"]
        self.image = self.original_image

        self.position = CoordinatesObject(0, 0)
        tank_list.append(self)

    def kill_or_revive(self):
        """
        Функция для инициализации убийства танка
        """
        self.dead = not self.dead
        self.original_image =  (green_tank if self.team == "red" else yellow_tank)["dead" if self.dead else "alive"]

        self.image = self.original_image
        self.rotate(self.position.angle)

    def set_position(self, position: CoordinatesObject):
        self.position = position
        self.rotate_localy()

    def move(self, position: CoordinatesObject):
        if position.angle == 0:
            position.angle = 360
        elif position.angle > 360:
            position.angle = 90

        self.position = position

        connection.send({
            "command": "step",
            "what": "move_anyway",
            "team": self.team,
            "number": self.number,
            "position": self.position.to_json()
        })
    
    def rotate_localy(self):
        self.image = pygame.transform.rotate(self.original_image, self.position.angle - 90)

    def rotate(self, angle = None):
        coords = self.position
        coords.angle = angle if angle else coords.angle + 90
        self.move(coords)
        self.rotate_localy()

    def draw(self, surface: pygame.Surface):
        """
        Отрисовка танка на поверхности PyGame
        """
        surface.blit(self.image, (self.position.x  * cells["size"], self.position.y * cells["size"]))
    
    def add(self, move = {}):
        connection.send({
            "command": "init",
            "who": "tank",
            "number": self.number,
            "team": self.team,
            "move": move
        })

    def delete(self):
        connection.send({
            "command": "clear",
            "what": "tank",
            "number": self.number,
            "team": self.team
        })

tank_list: list[Tank] = []

def setList(new_list: list):
    """
    Устанавливает новый локальный список танков и их расположение
    """
    global tank_list
    tank_list = []
    for tank in new_list:
        newt = Tank(tank["team"], tank["number"], tank["dead"])
        newt.set_position(CoordinatesObject().from_json(tank["position"]))

def foundTank(x: int, y: int) -> (Tank | None):
    """
    Ищет танк на позиции
    """
    global tank_list
    for tank in tank_list:
        if tank.position.x == x and tank.position.y == y:
            return tank
    return None

active_tank: Tank = None
"""
Активный выбранный танк
"""