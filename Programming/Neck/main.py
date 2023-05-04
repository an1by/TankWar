import pygame
from pygame.locals import *
import sys
import manager

pygame.init()
pygame.mixer.init()

###
from utils import *
from tcpip import connection
import tanks
screen_size = (cells["size"] * cells["amount"], cells["size"] * cells["amount"])

screen = pygame.display.set_mode(screen_size) # 512, 576
pygame.display.set_caption('Танковый бой - Шея')

clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()

### Настраиваем пути текстур ###
lime_box = getImage("boxes/1")
green_box = getImage("boxes/2")
full = getImage("boxes/full")
river = getImage("boxes/river")

### Настраиваем шрифт ###
sub_cells_amount = cells["amount"] * cells["size"] // cells["sub_size"]
for i in range(0, sub_cells_amount):
    for j in range(0, sub_cells_amount):
        boxSprite = pygame.sprite.Sprite()
        boxSprite.image = (lime_box if j%2 == i%2 else green_box)
        boxSprite.rect = (lime_box if j%2 == i%2 else green_box).get_rect()
        boxSprite.rect.x = i*cells["sub_size"]
        boxSprite.rect.y = j*cells["sub_size"]
        boxSprite.custom_type = ("lime_box" if j%2 == i%2 else "green_box")
        boxSprite.custom_state = "empty"
        allSprites.add(boxSprite)

def mainMenu():
    what_to_change = "obstacles"
    timer = 0
    ten_timer = 0
    while True:
        clock.tick(60)

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
            arr = []
            for sprite in allSprites:
                if sprite.custom_state != "empty":
                    position = {
                        "x": sprite.rect.x // cells["sub_size"], 
                        "y": sprite.rect.y // cells["sub_size"]
                    }
                    arr.append({"position": position, "type": sprite.custom_state})
            manager.update_field(arr)
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
                    x, y = posX//cells["sub_size"], posY//cells["sub_size"]
                    match what_to_change:
                        case "obstacles":
                            if event.button == 1:
                                x = x * cells["sub_size"]
                                y = y * cells["sub_size"]
                                for sprite in allSprites:
                                    if sprite.rect.x == x and sprite.rect.y == y:
                                        match (sprite.custom_state):
                                            case "empty":
                                                sprite.custom_state = "full"
                                                sprite.image = full
                                            case "full":
                                                sprite.custom_state = "river"
                                                sprite.image = river
                                            case "river":
                                                sprite.custom_state = "empty"
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
                    pass
        
        for dt in tanks.tank_list:
            dt.draw(screen)
        allSprites.update()
        allSprites.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    mainMenu()