import pygame
from utils import draw_text, get_text_render, cells
from storage import *
import tanks

hints = {
    "none": ['Ожидайте второго игрока'],
    "non_step": ["Ожидайте хода второго игрока"],
    "step": ['Нажмите на танк для', 'взаимодействия с ним'],
    "move": ['Нажмите на подсвеченную', 'клетку чтобы передвинуть', 'танк',
             '',
             'Для переключения режима', 'нажмите на кнопку', '"Огонь"'
             ],
    "rotate": ["Нажмите на одну из", "стрелок чтобы повернуть танк"],
    "fire": ["Нажмите на подсвеченную", "клетку чтобы выстрелить",
             '',
             'Для переключения режима', 'нажмите на кнопку', '"Передвижение"'
             ]
}

def draw_hint(surface: pygame.Surface, current_choose: str | None, current_step: bool | None):
    global hints
    hint = None
    match current_choose:
        case "move" | "fire" | "rotate":
            if current_step == True:
                hint = hints[current_choose]
        case _:
            match current_step:
                case None:
                    hint = hints["none"]
                case False:
                    hint = hints["non_step"]
                case True:
                    hint = hints["step"]
    if hint:
        for i, h in enumerate(hint):
            rendered = get_text_render(h)
            draw_text(surface, rendered, 0, cells["size"] * - 4.5 + (i * rendered.get_height() * 1.1), orientation="left")

alph = 'АБВГДЕЖЗ'

def draw_words(surface: pygame.Surface, sb_h):
    for index, word in enumerate('АБВГДЕЖЗ'):
        rendered = utils.get_text_render(word)
        utils.draw_text(surface, rendered, (rendered.get_width() + cells["size"] * 0.8) // 2 + (cells["size"] * (index - 4)), sb_h - cells["size"] * 0.8, orientation="up")
    for index in range(8):
        rendered = utils.get_text_render(index + 1)
        utils.draw_text(surface, rendered, (rendered.get_width() + cells["size"] * 0.8) // 2 + (cells["size"] * - 5), sb_h + cells["size"] * (index + 0.2), orientation="up")
                    

stat_hints = {
    360: "Запад",
    0: "Запад",
    90: "Север",
    180: "Восток",
    270: "Юг"
}

def draw_current_tank(surface: pygame.Surface):
    if tanks.active_tank:
        text_height = get_text_render("В").get_height()
        tank_image = pygame.transform.scale(tanks.active_tank.image, (text_height, text_height))
        
        pos = tanks.active_tank.position
        draw_text(surface, f'Выбран танк {"зеленых" if tanks.active_tank.team == "red" else "желтых"}', 0, cells["size"] * 3 - (text_height * 1.1), orientation="left")
        draw_text(surface, tank_image, 0, cells["size"] * 3, orientation="left")
        draw_text(surface, f'{alph[pos.x]}-{str(pos.y + 1)} | {stat_hints[pos.angle]}', text_height * 1.1, cells["size"] * 3, orientation="left")
