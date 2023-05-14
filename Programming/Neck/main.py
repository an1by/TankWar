# Инициализация папки общих библиотек
import sys
sys.path.insert(1, '../Libraries')

from tcpip import connection
connection.connect('play.aniby.net', 3030)
connection.init("manager")

from time import sleep
import pygame
from pygame.locals import *
import manager

cells = {
    "size": 64,
    "amount": 8
}

pygame.init()
pygame.mixer.init()

screen_size = (cells["size"] * cells["amount"], cells["size"] * cells["amount"])

screen = pygame.display.set_mode(screen_size) # 512, 576
pygame.display.set_caption('Танковый бой - Шея')

clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()

###
from utils import *
from maps import map_list

import tanks

### Настраиваем пути текстур ###
boxes = {
    "lime": getImage("boxes/1"),
    "green": getImage("boxes/2"),
    "full": getImage("boxes/full"),
    "river": getImage("boxes/river")
}

### Настраиваем поле ###
def get_box(x, y, type):
    boxSprite = pygame.sprite.Sprite()
    boxSprite.image = boxes["lime" if x%2 == y%2 else "green"] if type == "empty" else boxes[type]
    boxSprite.rect = boxSprite.image.get_rect()
    boxSprite.rect.x = x*cells["size"]
    boxSprite.rect.y = y*cells["size"]
    boxSprite.custom_type = type
    return boxSprite

def fill_field():
    global allSprites
    allSprites = pygame.sprite.Group()
    for x in range(0, cells["amount"]):
        for y in range(0, cells["amount"]):
            allSprites.add(
                get_box(x, y, "empty")
            )

# def set_obstacles(obstacles):
#     fill_field()
#     for obstacle in obstacles:
#         x = x * cells["size"]
#         y = y * cells["size"]
#         for sprite in allSprites:
#             if sprite.rect.x == x and sprite.rect.y == y:
#                 new_sprite = get_box(x, y,
#                     "full" if sprite.custom_type == "empty" else 
#                     (
#                         "river" if sprite.custom_type == "river" else 
#                         "empty"
#                     )
#                 )
#                 sprite.custom_type, sprite.image = new_sprite.custom_type, new_sprite.image

fill_field()

def mainMenu():
    what_to_change = "obstacles"
    timer = 0
    ten_timer = 0
    while True:
        clock.tick(60)
        to_update = []

        if timer < 10:
            timer += 1
        else:
            if connection.connected:
                for received in connection.receive():
                    if received and received["action"]:
                        match (received['action']):
                            # case "set_obstacles":
                            #     set_obstacles(received["obstacles"])
                            case "set_tanks":
                                tanks.setList(received["tanks"])
                            case "fire_feedback":
                                obj = received["object"]
                                match obj["name"]:
                                    case "tank":
                                        founded_tank = tanks.getByNumber(obj["team"], obj["number"])
                                        if founded_tank:
                                            founded_tank.kill_or_revive()
                                            connection.send({
                                                "command": "step",
                                                "what": "dead_status",
                                                "status": founded_tank.dead,
                                                "number": founded_tank.number,
                                                "team": founded_tank.team
                                            })
                            case "move_tank":
                                founded_tank = tanks.getByNumber(received["team"], received["number"])
                                if founded_tank:
                                    founded_tank.move(
                                        CoordinatesObject().from_json(received["position"])
                                    )
            ten_timer += 1
            timer = 0

        if ten_timer >= 10:
            for sprite in allSprites:
                if sprite.custom_type != "empty":
                    position = {
                        "x": sprite.rect.x // cells["size"], 
                        "y": sprite.rect.y // cells["size"]
                    }
                    to_update.append({"position": position, "type": sprite.custom_type})
            manager.update_field(to_update)
            ten_timer = 0

        screen.fill((0, 0, 0))

        posX, posY = pygame.mouse.get_pos()

        for event in pygame.event.get():
            match (event.type):
                case pygame.QUIT:
                    connection.stop()
                    pygame.quit()
                    sys.exit()
                case pygame.MOUSEBUTTONDOWN:
                    x, y = posX//cells["size"], posY//cells["size"]
                    match what_to_change:
                        case "obstacles":
                            if event.button == 1:
                                x = x * cells["size"]
                                y = y * cells["size"]
                                for sprite in allSprites:
                                    if sprite.rect.x == x and sprite.rect.y == y:
                                        new_sprite = get_box(x, y,
                                            "full" if sprite.custom_type == "empty" else 
                                            (
                                                "river" if sprite.custom_type == "river" else 
                                                "empty"
                                            )
                                        )
                                        sprite.custom_type, sprite.image = new_sprite.custom_type, new_sprite.image
                        case "tanks":
                            tank = tanks.foundTank(x, y)
                            if tanks.active_tank:
                                match event.button:
                                    case 2:
                                        tanks.active_tank.rotate()
                            else:
                                coords = CoordinatesObject(x,y)
                                coords.angle = 360
                                match event.button:
                                    case 1: # ЛКМ
                                        if tank:
                                            tanks.active_tank = tank
                                        else:
                                            tanks.Tank("red").add(coords.to_json())
                                    case 3: # ПКМ
                                        if not tank:
                                            tanks.Tank("blue").add(coords.to_json())
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            tanks.active_tank = None
                        case pygame.K_o:
                            what_to_change = "obstacles"
                        case pygame.K_t:
                            what_to_change = "tanks"
                    match what_to_change:
                        case "obstacles":
                            map = None
                            match event.key:
                                case pygame.K_1:
                                    map = map_list[0]
                                case pygame.K_2:
                                    map = map_list[1]
                                case pygame.K_3:
                                    map = map_list[2]
                                case pygame.K_0:
                                    connection.send({"command": "clear", "what": "obstacles"})
                                    fill_field()
                            if map:
                                for sprite in allSprites:
                                    x = sprite.rect.x // cells["size"]
                                    y = sprite.rect.y // cells["size"]
                                    new_sprite = get_box(x, y, "empty")
                                    for obs in map:
                                        if x == obs["position"]["x"] and y == obs["position"]["y"]:
                                            new_sprite = get_box(x, y, obs["type"])
                                    sprite.custom_type, sprite.image = new_sprite.custom_type, new_sprite.image
                        case "tanks":
                            if tanks.active_tank:
                                angle = -1
                                to_x, to_y = 0, 0
                                match event.key:
                                    case pygame.K_DELETE:
                                        tanks.active_tank.delete()
                                        tanks.active_tank = None

                                    case pygame.K_RIGHT:
                                        angle = 360
                                    case pygame.K_UP:
                                        angle = 90
                                    case pygame.K_LEFT:
                                        angle = 180
                                    case pygame.K_DOWN:
                                        angle = 270

                                    case pygame.K_d:
                                        to_x = 1
                                    case pygame.K_w:
                                        to_y = -1
                                    case pygame.K_a:
                                        to_x = -1
                                    case pygame.K_s:
                                        to_y = 1
                                if angle >= 0 and angle != tanks.active_tank.position.angle:
                                    tanks.active_tank.rotate(angle)
                                elif to_x != 0 or to_y != 0:
                                    tanks.active_tank.move(
                                        CoordinatesObject(
                                            tanks.active_tank.position.x + to_x,
                                            tanks.active_tank.position.y + to_y,
                                            tanks.active_tank.position.angle
                                        )
                                    )
        
        allSprites.update()
        allSprites.draw(screen)
        for dt in tanks.tank_list:
            dt.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    mainMenu()