import pygame
from pygame.locals import *
from pygame_widgets import *
import os, time
import sys

### Инциализация PyGame ###
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Танковый бой - Клиент')
clock = pygame.time.Clock()
allSprites = pygame.sprite.Group()
display_info = pygame.display.Info()

### Основной экран ###
from utils import CoordinatesObject, cells
screen_size = (
    display_info.current_w,
    display_info.current_h
)
scren_coeff = 1080 / display_info.current_h
screen = pygame.display.set_mode(screen_size, FULLSCREEN)

### Constants ###
cell_size = cells["size"] * cells["amount"]
razdiscell = [
    int((display_info.current_w - cell_size) // 2),
    int((display_info.current_h - cell_size) // 2)
]

### Variables ###
game_status = "server_select" # main / game / settings / server_select

### Настраиваем директории ###
#rootPath = os.path.dirname(__file__)
#resourcesPath = os.path.join(rootPath, "resources")

### Инициализация моих импортов ###
import tcpip
import button
import utils
import tanks

### Настраиваем пути текстур ###
def getImage(name):
    return pygame.image.load("./resources/" + name + ".png").convert_alpha()

def getImageBox(name):
    return pygame.transform.scale(getImage(name), (cells["sub_size"], cells["sub_size"]))

# lime_box = getImageBox("lime_box")
# green_box = getImageBox("green_box")
box1 = getImageBox("boxes/1")
box2 = getImageBox("boxes/2")
obstacle = getImageBox("obstacle")
river = getImageBox("river")

screenScrollX = 0
screenScrollY = 0

###### Canvas'ы ######
### Canvas игры ###
game_canvas = pygame.Surface((cell_size, cell_size))

### Canvas меню ###
main_canvas = pygame.Surface((display_info.current_w, display_info.current_h))
server_select_canvas = pygame.Surface((cell_size, cell_size))

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
settings_button = button.Button(0, 0, getImage("button"), 1)
servers_buttons = []

cellmargin = round(cells["size"] * 0.2)
for index, server in enumerate(utils.servers):
    server_button = button.CanvasButton(
        cell_size - 40, cells["size"], # width, height
        cellmargin, cellmargin + (cells["size"] + cellmargin) * index, # x, y
        [80, 80, 80] if server["address"] != "" else [150, 150, 150], # Color
        { # additionals_to_coords
            "x": razdiscell[0],
            "y": razdiscell[1]
        },
        [ # Contents
            {
                "text": "Сервер " + server["name"],
                "color": (255, 255, 255),
                "x": 10,
                "y": 30
            },
            {
                "text": "ping|" + server["address"] if server["address"] != "" else "",
                "color": (255, 255, 255),
                "x": cell_size - 186,
                "y": 30
            }
        ],
        { # Transparent
            "color": [60, 60, 60],
            "time": 0.5
        } if server["address"] != "" else None
    )
    servers_buttons.append(server_button)

def updateField():
    tcpip.send_data({"command"})

def main():
    global game_status
    global servers_buttons
    current_step = None # True: step / False: waiting / None: waiting in game start
    not_avalaible = {
        "timer": 0,
        "text": ""
    }
    timer = 0
    team = None
    step_time = 30
    current_cell = [-1, -1]
    received = None

    colors = {
        "me": (97, 65, 67),
        "enemy": (52, 69, 76)
    }

    while True:
        clock.tick(60)
        
        if not_avalaible["timer"] > 0:
            not_avalaible["timer"] -= 1
        
        if timer < 10:
            timer += 1
        else:
            for received in tcpip.get_data():
                if received and received["action"]:
                    print(received)
                    match (received['action']):
                        case "step_feedback":
                            current_step = None if received['step'] == "none" else received['step']
                            step_time = received['time']
                        case "init":
                            team = received["team"]
                        case "set_tanks":
                            tanks.setList(received["tanks"])
                        case "move_tank":
                            founded_tank = tanks.getByNumber(received["team"], received["number"])
                            if founded_tank:
                                founded_tank.move(
                                    CoordinatesObject(
                                        received["position"]["x"],
                                        received["position"]["y"]
                                    )
                                )
            timer = 0
            #updateField()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_status == "game" and current_step == True:
                    margin_w = razdiscell[0]
                    margin_h = cells["size"] * 0.5
                    posX, posY = pygame.mouse.get_pos()
                    posX -= margin_w
                    posY -= margin_h
                    if 0 <= posX < cells["size"] * cells["amount"] and 0 <= posY < cells["size"] * cells["amount"]:
                        position = CoordinatesObject(int(posX // cells["size"]), int(posY // cells["size"])) # 0, 1, 2, 3, 4, 5, 6, 7
                        if not tanks.active_tank:
                            founded_tank = tanks.foundTank(position)
                            if founded_tank.team == team:
                                tanks.active_tank = tanks.foundTank(position)
                        else:
                            tanks.active_tank.move(position)
                            tcpip.send_data({
                                "command": "step",
                                "what": "move",
                                "number": tanks.active_tank.number
                            })
                            tanks.active_tank = None
                    
        allSprites.update()
        match (game_status):
            case "game":
                # Фон\
                screen.fill((108, 108, 108))
                # Размеры
                sb_w = razdiscell[0]
                sb_h = cells["size"] * 0.5
                # Обводка
                pygame.draw.rect(screen, (65, 65, 65), (sb_w - 20, sb_h - 20, sb_w + cell_size//2.29 , sb_h + cell_size * 0.988))
                # Применение игрового канваса
                screen.blit(game_canvas, (sb_w, sb_h))
                # Отрисовка квадратов
                allSprites.draw(game_canvas)
                # Отрисовка танков
                for tank in tanks.tank_list:
                    tank.draw(game_canvas)
                
                
                if current_step != None:
                    display_pos = (display_info.current_w * 0.89, display_info.current_h * 0.83)
                    current_color = colors["me"] if current_step == True else colors["enemy"]
                    pygame.draw.circle(screen, current_color, display_pos, 130, 30)
                    utils.draw_text(screen, str(step_time) + "c" , current_color, display_pos[0], display_pos[1])
            case "server_select":
                screen.blit(main_canvas, (0, 0))
                main_canvas.fill((37, 250, 73))
                sb_w = razdiscell[0]
                sb_h = razdiscell[1]
                main_canvas.blit(server_select_canvas, (sb_w, sb_h))
                server_select_canvas.fill((100, 100, 100))
                
                alpha = round(255 / 120 * not_avalaible["timer"])
                text = utils.font.render(not_avalaible["text"], True, (255, 255, 255))
                text.set_alpha(alpha if alpha <= 255 else 255)
                text_rect = text.get_rect(center = (display_info.current_w//2, 40))
                main_canvas.blit(text, text_rect)
                
                ### Server Canvas ###
                for server_button in servers_buttons:
                    if server_button.draw(server_select_canvas, (timer == 0)):
                        #game_status = "game"
                        not_avalaible["timer"] = 200
                        not_avalaible["text"] = ""
                        match (server_button.contents[0]["text"].replace("Сервер ", "")):
                            case "СССР":
                                not_avalaible["text"] = "СССР не найден, сервер недоступен."
                            case "Пиндосостан":
                                not_avalaible["text"] = "Роскомнадзор заблокировал сервер."
                            case "КГБ":
                                not_avalaible["text"] = "Подключение не удалось, обратитесь к подполковнику Путину."
                            case "ФСБ":
                                not_avalaible["text"] = "СОБР уже выехал, ожидайте под вашими окнами."
                            case _:
                                tcpip.connect_default()
                                tcpip.init()
                                game_status = "game"
                # if settings_button.draw(main_canvas):
                #     game_status = "game"
            case "settings":
                pass
        pygame.display.flip()
        received = None

main()