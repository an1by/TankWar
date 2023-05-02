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
import tcpip
import utils
import tanks
import obstacles
from credits import Credits
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
    game_status = "menu" # menu / game / settings / server_select
    # global servers_buttons
    current_step = None # True: step / False: waiting / None: waiting in game start
    not_available = {
        "timer": 0,
        "text": ""
    }
    timer = 0
    team = None
    step_time = 30
    current_choose = "" # "" - ничего, move = передвижение, fire = стрельба, rotate = поворот
    received = None

    colors = {
        "me": (97, 65, 67),
        "enemy": (52, 69, 76)
    }

    temp_position = None

    while True:
        clock.tick(60)
        
        if not_available["timer"] > 0:
            not_available["timer"] -= 1
        
        if timer < 10:
            timer += 1
        else:
            for received in tcpip.get_data():
                if received and received["action"]:
                    match (received['action']):
                        case "step_feedback":
                            current_step = None if received['step'] == "none" else received['step']
                            if received["step"] == "none" or not received["step"]:
                                current_choose = ""
                            step_time = received['time']
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
                if game_status == "game" and current_step == True:
                    angle = -1
                    match event.key:
                        case pygame.K_e:
                            if tanks.active_tank and current_choose == "move" or current_choose == "fire":
                                current_choose = "move" if current_choose == "fire" else "fire"
                        case pygame.K_ESCAPE:
                            if tanks.active_tank and current_step:
                                tanks.active_tank = None
                                temp_position = None
                                current_choose = ""
                        case pygame.K_d:
                            angle = 360
                        case pygame.K_w:
                            angle = 90
                        case pygame.K_a:
                            angle = 180
                        case pygame.K_s:
                            angle = 270
                    if angle >= 0 and current_choose == "rotate" and temp_position != None:
                        temp_position.angle = angle
                        tanks.active_tank.move_and_send(temp_position)
                        temp_position = None
                        tanks.active_tank = None
                        current_step = False
                    angle = -1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_status == "game" and current_step == True:
                    margin_w = razdiscell[0]
                    margin_h = cells["size"] * 0.5
                    posX, posY = pygame.mouse.get_pos()
                    posX -= margin_w
                    posY -= margin_h
                    if 0 <= posX < cells["size"] * cells["amount"] and 0 <= posY < cells["size"] * cells["amount"]:
                        position = CoordinatesObject(int(posX // cells["size"]), int(posY // cells["size"])) # 0, 1, 2, 3, 4, 5, 6, 7
                        founded_tank = tanks.foundTank(position)
                        if tanks.active_tank:
                            match (current_choose):
                                case "move":
                                    if tanks.active_tank.can_move(position):
                                        temp_position = position
                                        current_choose = "rotate"
                                case "fire":
                                    if tanks.active_tank.fire_and_send(position):
                                        current_step = False
                                case "rotate":
                                    pass
                                case _:
                                    pass
                        if founded_tank and founded_tank.team == team and not founded_tank.dead and current_step:
                            tanks.active_tank = founded_tank
                            current_choose = "move"
                        elif current_step and temp_position and current_choose == "rotate":
                            pass
                        else:
                            tanks.active_tank = None

        # Drawing
        allSprites.update()
        match (game_status):
            case "game":
                # Фон\
                screen.fill((108, 108, 108))
                # Размеры
                sb_w = razdiscell[0]
                sb_h = cells["size"] * 0.5
                # Обводка
                pygame.draw.rect(screen, (65, 65, 65), (sb_w - 20, sb_h - 20, sb_w + all_cells_size//2.29 , sb_h + all_cells_size * 0.988))
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
                    current_color = colors["me"] if current_step == True else colors["enemy"]
                    pygame.draw.circle(screen, current_color, display_pos, 130, 30)
                    utils.draw_text(screen, str(step_time) + "c" , display_pos[0], display_pos[1], text_color=current_color)

                    if game_status == "game" and current_step == True and tanks.active_tank:
                        match current_choose:
                            case "move", "fire":
                                if change_choose_button.draw(screen, False):
                                    current_choose = "move" if current_choose == "fire" else "fire"

            case "menu":
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill((37, 250, 73))
                main_canvas.blit(menu_canvas, (0, 0))
                menu_canvas.fill((100, 100, 100))

                utils.draw_text(menu_canvas, "Танковый бой", screen_size[0], cells["size"]*1.5)
                if menu_buttons["play"].draw(menu_canvas):
                    game_status = "server_select"
                if menu_buttons["settings"].draw(menu_canvas):
                    game_status = "settings"
                if menu_buttons["authors"].draw(menu_canvas):
                    game_status = "authors"

            case "authors":
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill((37, 250, 73))
                main_canvas.blit(authors_canvas, (0, 0))
                authors_canvas.fill((100, 100, 100))
                credits.draw(authors_canvas)

            case "settings":
                # settings_buttons
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill((37, 250, 73))
                main_canvas.blit(settings_canvas, (0, 0))
                settings_canvas.fill((100, 100, 100))

                for key in settings_buttons.keys():
                    if settings_buttons[key].draw(settings_canvas):
                        settings_buttons[key].switch()


            case "server_select":
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill((37, 250, 73))
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
                            tcpip.connect(server_button.server["address"], server_button.server["port"])
                            tcpip.init()
                            game_status = "game"
                        elif "not_available" in server_button.server:
                            not_available["timer"] = 100
                            not_available["text"] = server_button.server["not_available"]
                # if settings_button.draw(main_canvas):
                #     game_status = "game"
            case "settings":
                pass

        if up_buttons["exit"].draw(screen):
            pygame.quit()
            sys.exit()
        if up_buttons["iconify"].draw(screen):
            pygame.display.iconify()
        match (game_status):
            case "settings" | "server_select" | "authors":
                if up_buttons["back"].draw(screen):
                    game_status = "menu"
            case "game":
                if up_buttons["back"].draw(screen):
                    game_status = "server_select"
        pygame.display.flip()
        received = None

main()