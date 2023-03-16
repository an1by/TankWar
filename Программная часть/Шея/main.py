import pygame
from pygame.locals import *
import os
import sys

pygame.init()
pygame.mixer.init()

motion = "stop"

screen = pygame.display.set_mode((512, 512))
pygame.display.set_caption('Танковый бой - Шея')

clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()

### Настраиваем директории ###
rootPath = os.path.dirname(__file__)
resourcesPath = os.path.join(rootPath, "resources")

### Настраиваем пути текстур ###
ground512 = pygame.image.load(os.path.join(resourcesPath, "background.png"))
box = pygame.image.load(os.path.join(resourcesPath, "box.png"))
box = pygame.transform.scale(box, (64, 64))
boxSprite = pygame.sprite.Sprite()
boxSprite.image = box
boxSprite.rect = box.get_rect()

### Настраиваем шрифт ###
font1 = pygame.font.SysFont('calibri', 36)

fakeScreen = screen.copy()
testSurface = pygame.Surface((512, 512))

screenScrollX = 0
screenScrollY = 0

for i in range(0,8):
    alph = [0,2,4,6] if i%2==0 else [1,3,5,7]
    for j in alph:
        boxSprite = pygame.sprite.Sprite()
        boxSprite.image = box
        boxSprite.rect = box.get_rect()
        boxSprite.rect.x = i*64
        boxSprite.rect.y = j*64
        allSprites.add(boxSprite)

def mainMenu():
    global motion
    while True:
        clock.tick(60)

        screen.fill((0, 0, 0))

        # posX, posY = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                motion = "stop"

        # screen.blit(player, (0,0))
        fakeScreen.blit(ground512, (0, 0))
        allSprites.update()
        allSprites.draw(fakeScreen)
        screen.blit(pygame.transform.scale(fakeScreen, (512, 512)), (screenScrollX, screenScrollY))
        pygame.display.flip()


mainMenu()