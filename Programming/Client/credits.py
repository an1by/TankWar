import pygame
from storage import screen_size
from utils import draw_text, get_text_render, arial_font

lvg = "Лукьянов Владислав Геннадьевич"
pav = "Павлиди Дмитрий (aniby.net)"
kot = "Котов Евгений"
den = "Родионов Даниил"
egor = "Литвинов Егор"
shev = "Никита Шевцов"
titres = [
    ["ДЛЯ ВАС СТАРАЛАСЬ", ["Команда Краснодарского ПКУ"]],
    ["", ""],

    ["Руководитель проекта", lvg],

    ["Программа клиента", pav],
    ["Серверная часть", pav],

    ["Дизайн", [shev, pav]],

    ["Механическое поле", [kot, egor, den, shev]],
    ["Управление танками на поле", [kot, pav, egor, den]],

    ["Распознавание объектов", [egor, pav]]
]

ud_arial = pygame.font.SysFont('arial', 36)
ud_arial.set_underline(True)

class Credits(object):
    def __init__(self):
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA, 32).convert_alpha()
        self.multiplier = 2.5
        self.timer = 0

    def reset(self):
        self.timer = 0

    def draw(self, surface: pygame.Surface):
        self.timer += 1
        self.canvas.fill((0,0,0,0))
        k = 0
        lower_pos = 10**4
        for index, titers in enumerate(titres):
            titles = [
                get_text_render(titers[0], font=ud_arial)
            ]
            if isinstance(titers[1], list):
                for t in titers[1]:
                    titles.append(get_text_render(t))
            else:
                titles.append(get_text_render(titers[1]))
            sw, sh = surface.get_size()
            th = titles[0].get_height()
            y = self.timer * self.multiplier
            if index > 0:
                y -= (index * 2 + k) * th
            for i in range(0, len(titles)):
                tw = titles[i].get_width()
                draw_text(self.canvas, titles[i], (sw - tw) // 2, sh + th * i - y)
                if i > 1:
                    k += 1
            if index == len(titres) - 1:
                lower_pos = sh + th - y
            k += 1
        surface.blit(self.canvas, (0, 0))
        if lower_pos <= 0:
            self.reset()
            return True
        return False