import pygame
from pygame.locals import *
import os
import sys
import manager

pygame.init()
pygame.mixer.init()

###
cells = {
    "size": 64,
    "sub_size": 32,
    "amount": 8
}
screen_size = (cells["size"] * cells["amount"], cells["size"] * cells["amount"])
motion = "stop"

screen = pygame.display.set_mode(screen_size) # 512, 576
pygame.display.set_caption('Танковый бой - Шея')

clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()

### Настраиваем директории ###
rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

### Настраиваем пути текстур ###
def getImage(name):
    image = pygame.image.load(os.path.join(resourcesPath, name + ".png"))
    return pygame.transform.scale(image, (cells["sub_size"], cells["sub_size"]))

lime_box = getImage("lime_box")
green_box = getImage("green_box")
obstacle = getImage("obstacle")
river = getImage("river")

### Настраиваем шрифт ###
font1 = pygame.font.SysFont('calibri', 36)

testSurface = pygame.Surface(screen_size)

screenScrollX = 0
screenScrollY = 0

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
    global motion
    timer = 0
    while True:
        clock.tick(60)

        if timer < 100:
            timer += 1
        else:
            timer = 0
            arr = []
            for sprite in allSprites:
                if sprite.custom_state != "empty":
                    start_pos = [
                        sprite.rect.x // cells["sub_size"], 
                        sprite.rect.y // cells["sub_size"]
                    ]
                    end_pos = [
                        start_pos[0] + cells["sub_size"] // cells["size"], 
                        start_pos[1] + cells["sub_size"] // cells["size"], 
                    ]
                    arr.append({"positions": [start_pos, end_pos], "state": sprite.custom_state})
            manager.update_field(arr)

        screen.fill((0, 0, 0))

        posX, posY = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                motion = "stop"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x = (posX//cells["sub_size"])*cells["sub_size"]
                    y = (posY//cells["sub_size"])*cells["sub_size"]
                    for sprite in allSprites:
                        if sprite.rect.x == x and sprite.rect.y == y:
                            match (sprite.custom_state):
                                case "empty":
                                    sprite.custom_state = "obstacle"
                                    sprite.image = obstacle
                                    break
                                case "obstacle":
                                    sprite.custom_state = "river"
                                    sprite.image = river
                                    break
                                case "river":
                                    sprite.custom_state = "empty"
                                    sprite.image = (lime_box if sprite.custom_type == "lime_box" else green_box)
                                    break
                            break
                        
        allSprites.update()
        allSprites.draw(screen)
        pygame.display.flip()


mainMenu()