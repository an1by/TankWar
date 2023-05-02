import pygame
from storage import settings_buttons
from utils import CoordinatesObject, cells, getImage
import tcpip, obstacles

green_tank = {
    "alive": getImage('tanks/green'),
    "dead": getImage('tanks/green_dead'),
    "dendy_alive": getImage('tanks/dendy/green'),
    "dendy_dead": getImage('tanks/dendy/green_dead')
}

yellow_tank = {
    "alive": getImage('tanks/yellow'),
    "dead": getImage('tanks/yellow_dead'),
    "dendy_alive": getImage('tanks/dendy/yellow'),
    "dendy_dead": getImage('tanks/dendy/yellow_dead')
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
    def __init__(self, team: str, number: int, dead: bool):
        """
        Инициализация танков
        """
        self.team = team
        self.number = number
        self.dead = dead

        path = (green_tank if team == "red" else yellow_tank)[
            ("dendy_" if settings_buttons["dendy"].current_value == 0 else "") + "alive"
        ]
        self.original_image = pygame.transform.scale(path, (72, 72))
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
        path = (green_tank if self.team == "red" else yellow_tank)[
            ("dendy_" if settings_buttons["dendy"].current_value == 0 else "") + "dead"
        ]
        self.original_image = pygame.transform.scale(path, (72, 72))
        self.image = self.original_image
        self.rotate(self.position.angle)

    def move_and_send(self, position: CoordinatesObject):
        """
        Выполняет передвижение танка и отправляет запрос на сервер при удачной проверке
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

    def rotate(self, angle: float):
        """
        Поворот изображения танка
        """
        self.image = pygame.transform.rotate(self.original_image, angle - 90)

    def set_position(self, position: CoordinatesObject):
        """
        Принудительно устанавливает локальную позицию танка
        """
        self.position.x, self.position.y = position.x, position.y
        if position.angle:
            self.position.angle = position.angle
            self.rotate(position.angle)

    def move(self, position: CoordinatesObject):
        """
        Устанавливает локальную позицию танка при удачной проверке
        """
        if self.can_move(position):
            self.set_position(position)
            return True
        return False

    def can_move(self, position: CoordinatesObject):
        """
        Проверка возможности передвижения на позицию
        """
        if self.dead:
            return False
        moving = abs(self.position.x - position.x) + abs(self.position.y - position.y)
        if moving == 1:
            if obstacles.foundObstacle(position):
                return False
            for tank in tank_list:
                if tank.position.x == position.x and tank.position.y == position.y:
                    return False
            return True
        return False
    
    def get_ranges(self):
        """
        Диапозоны расположения клеток для возможного обстрела
        """
        match self.position.angle:
            case 90: # Север
                return [
                    range(-1, 2),
                    range(-3, 0)
                ]
            case 270: # Юг
                return [
                    range(-1, 2),
                    range(1, 4)
                ]
            case 180: # Запад
                return [
                    range(-3, 0),
                    range(-1, 2)
                ]
            case _: # Djcnjr
                return [
                    range(1, 4),
                    range(-1, 2)
                ]

    # def raycast(self, position):
    #     arr = []
    #     rx = abs(self.position.x - position.x)
    #     ry = abs(self.position.y - position.y)
    #     k = ry / rx if rx != 0 else 0
    #     for x in range(self.position.x, position.x + 1):
    #         y = k * x
    #         tank = foundTank(CoordinatesObject(x, y))
    #         if tank != None and tank != self:
    #             arr.append(tank)
    #     return arr

    def can_fire(self, position: CoordinatesObject):
        """
        Проверка возможности стрельбы по позиции
        """
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
                    # for obstacle in obstacles.raycastTrajectory(
                    #     self.position,
                    #     new_position
                    # ):
                    #     if obstacle.type == "full":
                    #         return False
                    if obstacles.foundObstacle(new_position):
                        return False
                    found = foundTank(new_position)
                    if found and (found.team == self.team or found.dead):
                        return False
                    return True
        return False

    def fire_and_send(self, position: CoordinatesObject):
        """
        Выполняет выстрел и отправляет запрос на сервер при удачной проверке
        """
        if self.can_fire(position):
            tcpip.send_data({
                "command": "step",
                "what": "fire",
                "number": self.number,
                "position": position.to_json()
            })
            return True
        return False

    def draw(self, surface: pygame.Surface, current_choose: str):
        """
        Отрисовка танка на поверхности PyGame
        """
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

def getByNumber(team: str, number: int) -> (Tank | None):
    """
    Ищет танк по номеру и команде
    """
    for tank in tank_list:
        if tank.number == number and tank.team == team:
            return tank
    return None

def foundTank(position: CoordinatesObject) -> (Tank | None):
    """
    Ищет танк на позиции
    """
    for tank in tank_list:
        if tank.position.x == position.x and tank.position.y == position.y:
            return tank
    return None

active_tank: Tank = None
"""
Активный выбранный танк
"""