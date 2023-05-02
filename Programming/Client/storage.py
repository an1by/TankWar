import pygame, button, utils
from utils import cells

all_cells_size = cells["size"] * cells["amount"]
display_info = pygame.display.Info()
screen_size = (
    display_info.current_w,
    display_info.current_h
)
scren_coeff = 1080 / screen_size[1]
razdiscell = [
    int((screen_size[0] - all_cells_size) // 2),
    int((screen_size[1] - all_cells_size) // 2)
]

calibri_font = pygame.font.SysFont('calibri', 72)
arial_font = pygame.font.SysFont('arial', 16)

change_choose_button = button.CanvasButton(
    720, 80,
    410, 760,
    [80, 80, 80],
    [
        {
            "text": "Огонь/Двигаться",
            "color": (255, 255, 255),
            "x": 0,
            "y": 0
        }
    ],
    orientation="down",
    transparent={
        "color": [60, 60, 60],
        "time": 0.5
    }
)

servers = [
    {
        "name": "Aniby.NET",
        "address": "play.aniby.net",
        "port": 3030
    },
    {
        "name": "СССР",
        "not_available": "СССР не найден, сервер недоступен"
    },
    {
        "name": "Пиндосостан",
        "not_available": "Роскомнадзор заблокировал сервер"
    },
    {
        "name": "КГБ",
        "not_available": "Подключение не удалось, обратитесь к подполковнику Путину"
    },
    {
        "name": "ФСБ",
        "not_available": "СОБР уже выехал, ожидайте под вашими окнами"
    }
]

cellmargin = round(cells["size"] * 0.2)
servers_buttons = []
for index, server in enumerate(servers):
    server_button = button.ServerButton(
        all_cells_size - 40, cells["size"],
        cellmargin, cellmargin + (cells["size"] + cellmargin) * index,
        [80, 80, 80] if "address" in server else [150, 150, 150],
        servers[index],
        additionals_to_coords={
            "x": razdiscell[0],
            "y": razdiscell[1]
        },
        transparent={
            "color": [60, 60, 60],
            "time": 0.5
        } if "address" in server else None
    )
    servers_buttons.append(server_button)

up_buttons = {
    "exit": button.CanvasButton(
        cells["size"] // 2, cells["size"] // 2,
        screen_size[0] - cells["size"] // 2, 0,
        [80, 80, 80],
        [
            {
                "text": "X",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent={
            "color": [60, 60, 60],
            "time": 0.5
        },
        font=arial_font,
        orientation="center"
    ),
    "iconify": button.CanvasButton(
        cells["size"] // 2, cells["size"] // 2,
        screen_size[0] - cells["size"], 0,
        [80, 80, 80],
        [
            {
                "text": "_",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent={
            "color": [60, 60, 60],
            "time": 0.5
        },
        font=arial_font,
        orientation="center"
    ),
    "back": button.CanvasButton(
        cells["size"] // 2, cells["size"] // 2,
        screen_size[0] - cells["size"] * 1.5, 0,
        [80, 80, 80],
        [
            {
                "text": "<",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent={
            "color": [60, 60, 60],
            "time": 0.5
        },
        font=arial_font,
        orientation="center"
    )
}
settings_buttons = {
    "health": button.SwitchButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 2,
        [80, 80, 80],
        {
            "text": "Жизни",
            "color": (255, 255, 255),
            "x": 0,
            "y": 0
        },
        ["1", "2", "3"],
        transparent = {
            "color": [50, 50, 50],
            "time": 0.4
        },
        font = calibri_font
    ),
    "ai_game": button.SwitchButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 4,
        [80, 80, 80],
        {
            "text": "Игра с ИИ",
            "color": (255, 255, 255),
            "x": 0,
            "y": 0
        },
        ["V", "X"],
        transparent = {
            "color": [50, 50, 50],
            "time": 0.4
        },
        font = calibri_font
    ),
    "dendy": button.SwitchButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 6,
        [80, 80, 80],
        {
            "text": "Режим Dendy",
            "color": (255, 255, 255),
            "x": 0,
            "y": 0
        },
        ["V", "X"],
        transparent = {
            "color": [50, 50, 50],
            "time": 0.4
        },
        font = calibri_font
    )
}
menu_buttons = {
    "play": button.CanvasButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 2,
        [80, 80, 80],
        [
            {
                "text": "Играть",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent = {
            "color": [20, 20, 20],
            "time": 1
        },
        orientation = "center"
    ),
    "settings": button.CanvasButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 4,
        [80, 80, 80],
        [
            {
                "text": "Настройки",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent = {
            "color": [20, 20, 20],
            "time": 1
        },
        orientation = "center"
    ),
    "authors": button.CanvasButton(
        all_cells_size, cells["size"] * 1.5,
        (screen_size[0] - all_cells_size) // 2, cells["size"] * 6,
        [80, 80, 80],
        [
            {
                "text": "Авторы",
                "color": (255, 255, 255),
                "x": 0,
                "y": 0
            }
        ],
        transparent = {
            "color": [20, 20, 20],
            "time": 1
        },
        orientation = "center"
    )
}