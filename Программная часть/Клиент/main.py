import pygame
import button
import pygame_widgets
from findobjectinimage import findobject
from personplacement import placepersonprog
from pygame_widgets.textbox import TextBox
import time
from helpmain import programm
import json
from movefunc import move
#import tcpip
step = 0
choosetank = -1
chooseteam = ""
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 560
count = 0
cnt = 0
posblue = [[25,25,(0,0,255)],[176,25,(0,0,255)],[278,25,(0,0,255)]]
posred = [[25,486,(255,0,0)],[229,486,(255,0,0)],[331,486,(255,0,0)]]
colorblue = (0,0,255)
colorred = (255,0,0)

path = './png/data.png'
freeslots = [1,2,3,4,5,6,7,8,9,10,11,12]
occupiedslots = []
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
menu_state = "start"
debug_menu_state = ""
font = pygame.font.SysFont("arialblack", 24)
font1 = pygame.font.SysFont("arialblack", 40)
font2 = pygame.font.SysFont("arialblack", 18)
font3 = pygame.font.SysFont("arialblack", 22)
TEXT_COL = (0, 0, 0)
TEXT_COL_GREEN = (0, 255, 0)
TEXT_COL_RED = (255, 0, 0)

#load button images
start_img = pygame.image.load("./assets/start.png").convert_alpha()
fire_img = pygame.image.load("./assets/fire.png").convert_alpha()
step_img = pygame.image.load("./assets/step.png").convert_alpha()
reload_img = pygame.image.load("./assets/reload.png").convert_alpha()
move_img = pygame.image.load("./assets/movement.png").convert_alpha()
back_img = pygame.image.load("./assets/back.png").convert_alpha()
helper1 = pygame.image.load("./assets/helper.png").convert_alpha()
helper2 = pygame.image.load("./assets/car.png").convert_alpha()
choose = pygame.image.load("./assets/choose.png").convert_alpha()
#create button instances
start_button = button.Button(262, 150, start_img, 1)
fire_button = button.Button(612, 151, fire_img, 1)
step_button = button.Button(650, 405, step_img, 0.75)
reload_button = button.Button(677, 151, reload_img, 1)
move_button = button.Button(547, 151, move_img, 1)
back_button = button.Button(10, 10, back_img, 0.5)
commands = ['Синие', 'Красные']
def find():
	global freeslots
	global occupiedslots
	global path
	array = findobject(path)
	freeslots = array[0]
	occupiedslots = array[1]
def placementrandom(cnt):
	global count 
	global path
	count += 1
	path = place(int(cnt), count)
	
def chooseobject(step):
        global choosetank
        global chooseteam
        global posblue
        global posred
        if step % 2 == 0:
                command = "Синие"
                pos = posblue
        else:
                command = "Красные"
                pos = posred
        flag = False
        index = -1
        for i in range(len(posblue)):
                pygame.draw.circle(screen, posblue[i][2], (posblue[i][0]+10, posblue[i][1]+10), 15,5)
        for i in range(len(posred)):
                pygame.draw.circle(screen, posred[i][2], (posred[i][0]+10, posred[i][1]+10),15,5)
        while flag == False:
                print("Выберите танк")
                inputpos = programm()
                for i in range(len(pos)):
                        if inputpos[0][0] <= pos[i][0] + 25 and inputpos[0][0] >= pos[i][0] - 25 and inputpos[0][1] <= pos[i][1] + 25 and inputpos[0][1] >= pos[i][1] - 25:
                                index = i
                                flag = True
                                break
                if step > 0:
                        draw_text("Ход : " + commands[abs(step%2)], font, TEXT_COL, 575, 10)
                        draw_text("Повторите выбор", font3, TEXT_COL, 547, 100)
                
        choosetank = index
        chooseteam = command
        pos[index][2] = (0,255,0)
        
                                
                        
        
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))
#game loop
run = True
while run:
        place = pygame.image.load("./assets/Wide2.png").convert_alpha()
    # tracking for debug
        if (menu_state != debug_menu_state):
                debug_menu_state = menu_state


        screen.fill((12, 245, 132))
        if menu_state == "start":
                if start_button.draw(screen):
                        menu_state = "main"
        if menu_state == "main":
                screen.blit(place,(10,10))
                if step > 0:
                        draw_text("Ход : " + commands[abs(step%2 - 1)], font, TEXT_COL, 575, 10)
                for i in range(len(posblue)):
                        pygame.draw.circle(screen, colorblue, (posblue[i][0]+10, posblue[i][1]+10), 15,5)
                for i in range(len(posred)):
                        pygame.draw.circle(screen, colorred, (posred[i][0]+10, posred[i][1]+10),15,5)
                if step_button.draw(screen):
                        step += 1
                        for i in range(len(posblue)):
                                posblue[i][2] = colorblue
                        for i in range(len(posred)):
                                posred[i][2] = colorred
                        for i in range(len(posblue)):
                                pygame.draw.circle(screen, posblue[i][2], (posblue[i][0]+10, posblue[i][1]+10), 15,5)
                        for i in range(len(posred)):
                                pygame.draw.circle(screen, posred[i][2], (posred[i][0]+10, posred[i][1]+10 ),15,5)
                        chooseobject(step)
                        menu_state = "step"
        
    
    #check if the help menu is open
        elif menu_state == "step":
                screen.blit(place,(10,10))
                for i in range(len(posblue)):
                        pygame.draw.circle(screen, posblue[i][2], (posblue[i][0]+10, posblue[i][1]+10), 15,5)
                for i in range(len(posred)):
                        pygame.draw.circle(screen, posred[i][2], (posred[i][0]+10, posred[i][1]+10),15,5)
                if step > 0:
                        draw_text("Ход : " + commands[abs(step%2)], font, TEXT_COL, 575, 10)
                        draw_text("Выбранный танк", font2, TEXT_COL, 547, 50)
                        draw_text("Команда : " +" "+ chooseteam, font2, TEXT_COL, 547, 75)
                        draw_text("Серийный номер : " + ' № '+  str(choosetank + 1), font2, TEXT_COL, 547, 100)
                        draw_text("Действия", font2, TEXT_COL, 547, 125)
                        
                if move_button.draw(screen):
                        print("Move")
                        print(choosetank)
                        newpos = move(posblue,posred,choosetank,chooseteam, screen)
                        posred = newpos[0]
                        posblue = newpos[1]
                        menu_state = "main"
                if fire_button.draw(screen):
                        print("Fire")
                        menu_state = "main"
                if reload_button.draw(screen):
                        print("Reload")
                        menu_state = "main"
                        
        events = pygame.event.get()
            
  #event handler
        for event in events:
                if event.type == pygame.QUIT:
                        run = False
                if event.type == pygame.KEYDOWN and menu_state == 'main':
                        if event.key == pygame.K_:
                                menu_state = 'main'
        if menu_state == 'main':
                pygame_widgets.update(events)      
        pygame.display.update()
pygame.quit()
