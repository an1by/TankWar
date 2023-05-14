import pygame
from pygame.locals import *
from pygame_widgets import *
import sys

### Инциализация PyGame ###
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Танковый бой - Клиент')
clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()
display_info = pygame.display.Info()

### Основной экран ###
screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), FULLSCREEN)
from storage import *
"""
Главный Surface
"""

### Инициализация моих импортов ###
from utils import CoordinatesObject, cells
from tcpip import connection
import utils
import tanks
import obstacles
from credits import Credits
from hints import *
credits = Credits()

### Настраиваем пути текстур ###
box1 = utils.getImageBox("boxes/1")
box2 = utils.getImageBox("boxes/2")
obstacle = utils.getImageBox("obstacle")
river = utils.getImageBox("river")

screenScrollX = 0
screenScrollY = 0

###### Canvas'ы ######
### Canvas игры ###
game_canvas = pygame.Surface((all_cells_size, all_cells_size))

### Canvas меню ###
main_canvas = pygame.Surface(screen_size)
menu_canvas = pygame.Surface(screen_size)
authors_canvas = pygame.Surface(screen_size)
settings_canvas = pygame.Surface(screen_size)
server_select_canvas = pygame.Surface((all_cells_size, all_cells_size))

### Server Canvas ###


###### Настройка объектов ######
### Клетки на поле ###
sub_cells_amount = cells["amount"] * cells["size"] // cells["sub_size"]
for i in range(0, sub_cells_amount):
    for j in range(0, sub_cells_amount):
        boxSprite = pygame.sprite.Sprite()
        boxSprite.image = (box1 if j%2 == i%2 else box2)
        boxSprite.rect = (box1 if j%2 == i%2 else box2).get_rect()
        boxSprite.rect.x = i*cells["sub_size"]
        boxSprite.rect.y = j*cells["sub_size"]
        allSprites.add(boxSprite)

### Кнопки ###
# settings_button = button.Button(0, 0, getImage("button"), 1)

def main():
    """
    Основной рабочий класс
    """
    background_color = (120, 120, 120)
    game_status = "menu" # menu / game / settings / server_select
    # global servers_buttons
    current_step = None # True: step / False: waiting / None: waiting in game start

    game_winner = None

    not_available = {
        "timer": 0,
        "text": ""
    }
    timer = 0
    team = None
    step_time = 30
    pause = False
    current_choose = "" # "" - ничего, move = передвижение, fire = стрельба, rotate = поворот
    received = None

    colors = {
        "me": (101, 171, 59),
        "enemy": (195, 177, 60)
    }

    temp_position = None

    while True:
        clock.tick(60)
        
        if not_available["timer"] > 0:
            not_available["timer"] -= 1
        
        if timer < 10:
            timer += 1
        else:
            if connection.connected:
                for received in connection.receive():
                    if received and "action" in received:
                        match (received['action']):
                            case "step_feedback":
                                match received['step']:
                                    case "none":
                                        current_step = None
                                    case _:
                                        if current_step != received["step"]:
                                            temp_position = None
                                            tanks.active_tank = None
                                            current_choose = ""
                                            current_step = received["step"]
                                if not current_step:
                                    current_choose = ""
                                step_time = received['time']
                                if 'winner' in received:
                                    game_winner = received['winner']
                            case "init":
                                team = received["team"]
                                if team == "blue":
                                    colors["me"], colors["enemy"] = colors["enemy"], colors["me"]
                            case "set_tanks":
                                tanks.setList(received["tanks"])
                            case "set_obstacles":
                                obstacles.setList(received["obstacles"])
                            case "fire_feedback":
                                obj = received["object"]
                                match obj["name"]:
                                    case "none":
                                        pass
                                    case "obstacle":
                                        pass
                                    case "tank":
                                        tanks.getByNumber(obj["team"], obj["number"]).kill()
                            case "switch_pause":
                                pause = received["pause"]
                                if pause:
                                    tanks.active_tank = None
                                    temp_position = None
                                    current_choose = ""
                            case "move_tank":
                                founded_tank = tanks.getByNumber(received["team"], received["number"])
                                if founded_tank:
                                    founded_tank.move(
                                        CoordinatesObject().from_json(received["position"])
                                    )
            timer = 0
            #updateField()
        # Events Handler
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game_status == "game" and current_step == True and not pause:
                    angle = -1
                    match event.key:
                        case pygame.K_e:
                            if tanks.active_tank and current_choose == "move" or current_choose == "fire":
                                current_choose = "move" if current_choose == "fire" else "fire"
                                game_buttons["fire"].switch()
                        case pygame.K_ESCAPE:
                            if tanks.active_tank and current_step:
                                tanks.active_tank = None
                                temp_position = None
                                current_choose = ""
                        case pygame.K_d | pygame.K_RIGHT:
                            angle = 360
                        case pygame.K_w | pygame.K_UP:
                            angle = 90
                        case pygame.K_a | pygame.K_LEFT:
                            angle = 180
                        case pygame.K_s | pygame.K_DOWN:
                            angle = 270
                    if angle >= 0 and current_choose == "rotate" and temp_position != None:
                        temp_position.angle = angle
                        tanks.active_tank.move_and_send(temp_position)
                        temp_position = None
                        tanks.active_tank = None
                        # current_step = False
                    angle = -1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_status == "game" and current_step == True and not pause:
                    margin_w = razdiscell[0]
                    margin_h = cells["size"] * 1.5
                    posX, posY = pygame.mouse.get_pos()
                    posX -= margin_w
                    posY -= margin_h
                    if 0 <= posX < cells["size"] * cells["amount"] and 0 <= posY < cells["size"] * cells["amount"]:
                        position = CoordinatesObject(int(posX // cells["size"]), int(posY // cells["size"])) # 0, 1, 2, 3, 4, 5, 6, 7
                        print(position.to_json())
                        founded_tank = tanks.foundTank(position)
                        if tanks.active_tank:
                            match (current_choose):
                                case "move":
                                    if tanks.active_tank.can_move(position) and temp_position == None:
                                        temp_position = position
                                        current_choose = "rotate"
                                case "fire":
                                    if tanks.active_tank.fire_and_send(position):
                                        pass
                                        # current_step = False
                                case "rotate":
                                    pass
                                case _:
                                    pass
                        if founded_tank and founded_tank.team == team and not founded_tank.dead and current_step:
                            tanks.active_tank = founded_tank
                            current_choose = "move"
                            temp_position = None
                        elif current_step and temp_position and current_choose == "rotate":
                            pass
                        else:
                            tanks.active_tank = None

        # Drawing
        allSprites.update()
        match (game_status):
            case "game":
                # Фон\
                screen.fill(background_color)
                if game_winner:
                    utils.draw_text(screen, f'Выиграла команда {"Зеленых" if game_winner == "red" else "Желтых"}', 0, 0, orientation="center", font=calibri_font)
                    connection.stop()
                else:
                    # Размеры
                    sb_w = razdiscell[0]
                    sb_h = cells["size"] * 1.5
                    # Обводка
                    backgameimage = pygame.Surface((all_cells_size + cells["size"] * 0.5, all_cells_size + cells["size"] * 0.5))
                    backgameimage.fill((65, 65, 65))

                    # Отрисовка обозначений
                    utils.draw_text(screen, backgameimage, 0, -cells["size"] * 0.95 + sb_h, orientation = "up")
                    draw_words(screen, sb_h)
                    
                    # Отрисовка подсказок
                    draw_hint(screen, current_choose, current_step)

                    # Применение игрового канваса
                    screen.blit(game_canvas, (sb_w, sb_h))
                    # Отрисовка квадратов
                    allSprites.draw(game_canvas)
                    # Отрисовка препятсвтий
                    for obstacle in obstacles.obstacle_list:
                        obstacle.draw(game_canvas)
                    # Отрисовка танков
                    for tank in tanks.tank_list:
                        tank.draw(game_canvas, current_choose)

                    if current_step != None:
                        display_pos = (screen_size[0] * 0.89, screen_size[1] * 0.83)
                        circle_size = 130
                        pygame.draw.circle(screen, (colors["me"] if current_step == True else colors["enemy"]), display_pos, circle_size)
                        st_rendered = utils.get_text_render(step_time, font=calibri_font)
                        utils.draw_text(screen, st_rendered, display_pos[0] - st_rendered.get_width() // 2, display_pos[1] - st_rendered.get_height() // 2)

                        if current_step == True and not pause:
                            if game_buttons["skip"].draw(screen):
                                connection.send({
                                    "command": "step",
                                    "what": "skip"
                                })
                            if tanks.active_tank:
                                draw_current_tank(screen)
                                match current_choose:
                                    case "move" | "fire":
                                        if game_buttons["fire"].draw(screen):
                                            current_choose = "move" if current_choose == "fire" else "fire"
                                            game_buttons["fire"].switch()
                                    case "rotate":
                                        for key in game_buttons["moving"].keys():
                                            if game_buttons["moving"][key].draw(screen):
                                                angle = 0
                                                match (key):
                                                    case "up":
                                                        angle = 90
                                                    case "right":
                                                        angle = 360
                                                    case "down":
                                                        angle = 270
                                                    case "left":
                                                        angle = 180
                                                if temp_position != None:
                                                    temp_position.angle = angle
                                                    tanks.active_tank.move_and_send(temp_position)
                                                    temp_position = None
                                                    tanks.active_tank = None
                                                    # current_step = False
                                    case "move":
                                        for key in game_buttons["moving"].keys():
                                            if game_buttons["moving"][key].draw(screen):
                                                position = tanks.active_tank.position
                                                match (key):
                                                    case "up":
                                                        position.y += -1
                                                    case "right":
                                                        position.x += 1
                                                    case "down":
                                                        position.y += 1
                                                    case "left":
                                                        position.x += -1
                                                if tanks.active_tank.can_move(position) and temp_position == None:
                                                    temp_position = position
                                                    current_choose = "rotate"

            case "menu":
                screen.blit(main_canvas, (0, 0))
                main_canvas.blit(menu_canvas, (0, 0))
                menu_canvas.fill(background_color)

                pr_tankwar = utils.get_text_render("Танковый Бой", calibri_font)
                utils.draw_text(menu_canvas, pr_tankwar, 0, cells["size"] * 0.6, orientation="up")

                tg = pygame.transform.scale(tanks.green_tank["alive"], (72, 72))
                ty = pygame.transform.scale(tanks.yellow_tank["alive"], (72, 72))

                utils.draw_text(menu_canvas, tg, (pr_tankwar.get_width() + tg.get_width()) * -0.5, cells["size"] * 0.6, orientation="up")
                utils.draw_text(menu_canvas, ty, (pr_tankwar.get_width() + tg.get_width()) * 0.5, cells["size"] * 0.6, orientation="up")

                if menu_buttons["play"].draw(menu_canvas):
                    game_status = "server_select"
                if menu_buttons["settings"].draw(menu_canvas):
                    game_status = "settings"
                if menu_buttons["authors"].draw(menu_canvas):
                    game_status = "authors"

            case "authors":
                screen.blit(main_canvas, (0, 0))
                main_canvas.blit(authors_canvas, (0, 0))
                authors_canvas.fill(background_color)
                if credits.draw(authors_canvas):
                    game_status = "menu"

            case "settings":
                # settings_buttons
                screen.blit(main_canvas, (0, 0))
                main_canvas.blit(settings_canvas, (0, 0))
                settings_canvas.fill(background_color)

                for key in settings_buttons.keys():
                    if settings_buttons[key].draw(settings_canvas):
                        settings_buttons[key].switch()


            case "server_select":
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill(background_color)
                sb_w = razdiscell[0]
                sb_h = razdiscell[1]
                main_canvas.blit(server_select_canvas, (sb_w, sb_h))
                server_select_canvas.fill((100, 100, 100))
                
                alpha = round(255 / 6 * not_available["timer"])
                text = utils.arial_font.render(not_available["text"], True, (255, 255, 255))
                text.set_alpha(alpha if alpha <= 255 else 255)
                text_rect = text.get_rect(center = (screen_size[0]//2, 40))
                main_canvas.blit(text, text_rect)
                
                ### Server Canvas ###
                for server_button in servers_buttons:
                    if server_button.draw(server_select_canvas, (timer == 0)):
                        #game_status = "game"
                        if server_button.available():
                            connection.connect(server_button.server["address"], server_button.server["port"])
                            connection.init()
                            game_status = "game"
                        elif "not_available" in server_button.server:
                            not_available["timer"] = 100
                            not_available["text"] = server_button.server["not_available"]
                # if settings_button.draw(main_canvas):
                #     game_status = "game"

        utils.draw_text(screen, "© Краснодарское ПКУ (2023)", -15, 0, orientation="left_down", font=medium_arial_font)

        if up_buttons["exit"].draw(screen):
            pygame.quit()
            sys.exit()
        if up_buttons["iconify"].draw(screen):
            pygame.display.iconify()
        match (game_status):
            case "settings" | "server_select" | "authors":
                if up_buttons["back"].draw(screen):
                    if game_status == "authors":
                        credits.reset()
                    game_status = "menu"
            case "game":
                if up_buttons["back"].draw(screen):
                    game_status = "server_select"
                    game_winner = None
                    tanks.tank_list = []
                    obstacles.obstacle_list = []
                    current_choose = ""
                    team = None
                    pause = False
                    temp_position = None
                    step_time = 30
                    colors = {
                        "me": (97, 65, 67),
                        "enemy": (52, 69, 76)
                    }
                    connection.stop()
        pygame.display.flip()
        received = None

main()