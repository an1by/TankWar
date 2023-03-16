import pygame
from pygame.locals import *
import os
import sys
import tcpip

pygame.init()
pygame.mixer.init()

motion = "stop"

screen = pygame.display.set_mode((512, 512)) # 512, 576
pygame.display.set_caption('Танковый бой - Шея')

clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()

### Настраиваем директории ###
rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

### Настраиваем пути текстур ###
def getImage(name):
    image = pygame.image.load(os.path.join(resourcesPath, name + ".png"))
    return pygame.transform.scale(image, (64, 64))

lime_box = getImage("lime_box")
green_box = getImage("green_box")
obstacle = getImage("obstacle")
river = getImage("river")

### Настраиваем шрифт ###
font1 = pygame.font.SysFont('calibri', 36)

testSurface = pygame.Surface((512, 512))

screenScrollX = 0
screenScrollY = 0

for i in range(0,8):
    for j in range(0, 8):
        boxSprite = pygame.sprite.Sprite()
        boxSprite.image = (lime_box if j%2 == i%2 else green_box)
        boxSprite.rect = (lime_box if j%2 == i%2 else green_box).get_rect()
        boxSprite.rect.x = i*64
        boxSprite.rect.y = j*64
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
                arr.push({"positions": [sprite.rect.x, sprite.rect.y], "type": sprite.custom_type})
            tcpip.send_data({"command": "merge", "what": "obstacles", "list": arr})

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
                    # boxSprite = pygame.sprite.Sprite()
                    # boxSprite.image = box
                    # boxSprite.rect = box.get_rect()
                    # print(pygame.mouse.get_pos())
                    x = (posX//64)*64    #изменения тут
                    y = (posY//64)*64    #и тут
                    # print(boxSprite.rect.x,boxSprite.rect.y)
                    # allSprites.add(boxSprite)
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