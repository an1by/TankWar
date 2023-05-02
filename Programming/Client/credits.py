import pygame
from storage import screen_size
from utils import draw_text, get_text_render

lvg = "Лукьянов Владислав Геннадьевич"
pav = "Павлиди Дмитрий (aniby.net)"
kot = "Котов Евгений"
den = "Родионов Даниил"
egor = "Литвинов Егор"
titres = [
    ["Руководитель проекта", lvg],

    ["Программа клиента", pav],
    ["Серверная часть", pav],
    ["Дизайн", pav],

    ["Механическое поле", lvg],
    ["Управление танками на поле", kot],
    ["Взаимодействие с танками", kot],

    ["Распознавание объектов", egor]
]

class Credits(object):
    def __init__(self):
        self.canvas = pygame.Surface(screen_size, pygame.SRCALPHA, 32).convert_alpha()
        self.multiplier = 1 
        self.timer = 0

    def reset(self):
        self.timer = 0

    def draw(self, surface: pygame.Surface):
        self.timer += 1
        self.canvas.fill((0,0,0,0))
        k = 0
        lower_pos = 10**4
        for index, titer in enumerate(titres):
            titles = [
                get_text_render(titer[0]),
                get_text_render(titer[1])
            ]
            sw, sh = surface.get_size()
            tw1, tw2 = titles[0].get_width(), titles[1].get_width()
            th = titles[0].get_height()
            y = self.timer * self.multiplier
            if index > 0:
                y -= (index * 2 + k) * th
            draw_text(self.canvas, titles[0], (sw - tw1) // 2, sh - y)
            draw_text(self.canvas, titles[1], (sw - tw2) // 2, sh + th - y)
            if index == len(titres) - 1:
                lower_pos = sh + th - y
            k += 1
        surface.blit(self.canvas, (0, 0))
        return lower_pos <= 0