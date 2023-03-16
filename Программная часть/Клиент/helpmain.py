import pygame
from personplacement import placepersonprog
import time
pygame.init()

screen1 = pygame.display.set_mode((527, 527))
clock = pygame.time.Clock()
def programm():
    array = []
    for i in range(1):
        clock.tick(60)
        flag = False
        while flag == False:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:  # or MOUSEBUTTONDOWN depending on what you want.
                    pos = event.pos
                    if pos[0] <= 537 and pos[0] >= 10 and pos[1] <= 537 and pos[1] >= 10:
                        array.append([int(pos[0] - 10), int(pos[1] - 10)])
                        flag = True
                        break

        pygame.display.update()
    return array
