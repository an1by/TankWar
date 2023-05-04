import pygame
from pygame.locals import *
import sys
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
from tcpip import connection
import tanks


### Настраиваем пути текстур ###
lime_box = getImage("boxes/1")
green_box = getImage("boxes/2")
full = getImage("boxes/full")
river = getImage("boxes/river")

### Настраиваем шрифт ###
sub_cells_amount = cells["amount"] * cells["size"] // cells["size"]
for i in range(0, sub_cells_amount):
    for j in range(0, sub_cells_amount):
        boxSprite = pygame.sprite.Sprite()
        boxSprite.image = (lime_box if j%2 == i%2 else green_box)
        boxSprite.rect = (lime_box if j%2 == i%2 else green_box).get_rect()
        boxSprite.rect.x = i*cells["size"]
        boxSprite.rect.y = j*cells["size"]
        boxSprite.custom_type = ("lime_box" if j%2 == i%2 else "green_box")
        boxSprite.custom_type = "empty"
        allSprites.add(boxSprite)

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
                            case "set_tanks":
                                tanks.setList(received["tanks"])
                            case "fire_feedback":
                                obj = received["object"]
                                match obj["name"]:
                                    case "tank":
                                        tanks.getByNumber(obj["team"], obj["number"]).kill_or_revive()
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
                                        match (sprite.custom_type):
                                            case "empty":
                                                sprite.custom_type = "full"
                                                sprite.image = full
                                            case "full":
                                                sprite.custom_type = "river"
                                                sprite.image = river
                                            case "river":
                                                sprite.custom_type = "empty"
                                                sprite.image = (lime_box if sprite.custom_type == "lime_box" else green_box)
                                        break
                        case "tanks":
                            print(x, y)
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
                                            count = 0
                                            for t in tanks.tank_list:
                                                if t.team == "red":
                                                    count += 1
                                            tank = tanks.Tank("red", count, False)
                                            tank.move(coords)
                                    case 3: # ПКМ
                                        if not tank:
                                            count = 0
                                            for t in tanks.tank_list:
                                                if t.team == "blue":
                                                    count += 1
                                            tank = tanks.Tank("blue", count, False)
                                            tank.move(coords)
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_o:
                            what_to_change = "obstacles"
                        case pygame.K_t:
                            what_to_change = "tanks"
                    if what_to_change == "obstacles":
                        map = None
                        match event.key:
                            case pygame.K_1:
                                map = map_list[0]
                            case pygame.K_2:
                                map = map_list[1]
                            case pygame.K_3:
                                map = map_list[2]
                        if map:
                            for sprite in allSprites:
                                x = sprite.rect.x // cells["size"]
                                y = sprite.rect.y // cells["size"]
                                sprite.image = (lime_box if x%2 == y%2 else green_box)
                                sprite.custom_type = "empty"
                                for obs in map:
                                    if x == obs["position"]["x"] and y == obs["position"]["y"]:
                                        match (obs["type"]):
                                            case "full":
                                                sprite.custom_type = "full"
                                                sprite.image = full
                                            case "river":
                                                sprite.custom_type = "river"
                                                sprite.image = river
        
        allSprites.update()
        allSprites.draw(screen)
        for dt in tanks.tank_list:
            dt.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    mainMenu()