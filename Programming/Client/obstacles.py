from utils import CoordinatesObject, cells, getImage
import pygame
# type:
# - forest: лес. Непроходимо, 50% разброс.
# - full: гора/дом. Непроходимо, непростреливаемо
# - river: река. Непроходимо, простреливаемо

obstacle_images = {
    "river": getImage('boxes/river'),
    "full": getImage('boxes/full'),
    "forest": getImage('boxes/forest')
}

obstacle_list = []
class Obstacle(object):
    def __init__(self, x, y, type):
        self.position = CoordinatesObject(x, y)
        self.type = type
        self.image = pygame.transform.scale(obstacle_images[type], (cells["size"], cells["size"]))
        obstacle_list.append(self)
    
    def draw(self, surface):
        surface.blit(self.image, (self.position.x  * cells["size"], self.position.y * cells["size"]))

def foundObstacle(position: CoordinatesObject):
    global obstacle_list
    for obstacle in obstacle_list:
        if obstacle.position.x == position.x and obstacle.position.y == position.y:
            return obstacle
    return None

def raycastTrajectory(start: CoordinatesObject, end: CoordinatesObject):
    arr = []
    rx = abs(start.x - end.x)
    ry = abs(start.y - end.y)
    k = ry / rx if rx != 0 else 0
    for x in range(start.x, end.x + 1):
        y = k * x
        obstacle = foundObstacle(CoordinatesObject(x, y))
        if obstacle != None:
            arr.append(obstacle)
    return arr