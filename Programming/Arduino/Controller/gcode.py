def move(x, y) -> str:
    """
    Возвращает Gcode в виде строки для дальнейшей передачи
    """
    return ('G1 X{}Y{}'.format(x, y))

def rotate(angle) -> str:
    """
    Возвращает Gcode в виде для дальнейшей передачи
    """
    return ('G1 Z{}'.format(angle))

import math

def angle(x, y):
    """
    Вычисляет угол относитьно оси X
    """
    b = math.sqrt(x**2 + y**2)
    c = math.sqrt((x-1)**2 + y**2)
    if b != 0 and c != 0:
        alpha = math.acos((b**2 + c**2 - 1)/(2*b*c))
    else:
        alpha = 0 if x >= 0 else 180
    return alpha if y >= 0 else -alpha