import pygame
from utils import draw_text, get_text_render, cells
from storage import *

hints = {
    "none": ['Ожидайте второго игрока'],
    "non_step": ["Ожидайте хода второго игрока"],
    "step": ['Нажмите на танк для', 'взаимодействия с ним'],
    "move": ['Нажмите на подсвеченную', 'клетку чтобы передвинуть', 'танк'],
    "rotate": ["Нажмите на одну из", "стрелок чтобы повернуть танк"],
    "fire": ["Нажмите на подсвеченную", " клетку чтобы выстрелить"]
}

def draw_hint(surface, current_choose, current_step):
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
