# Подключение

![](./wires.jpg)

# Запуск

Диспетчер устройств, вкладка COM порты.
   найти COM порт в названии которого CH340 (или как_нибудь по другому определить). Далее **COM порт**.

## В нули

Запустить прогу **Gcode Universal Sender**, батник (если что в С:\\\\Program Files)

Верхний левый угол:

* Настроить COM порт
* Скорость (Baudrate) 115200

Выставить в ноль в ручную кнопочками (x+ x- ...)

## Запуск контроллера


В строке `uart = serial.Serial('/dev/ttyUSB0', 115200)` поменять `/dev/ttyUSB0` на нужный COM порт, например `COM7`

`$ python ./main.py`


### Зависимости

Прогу нужен `pyserial`, при отсутствии установить через **pip**

# Логи

`./uart.log`


