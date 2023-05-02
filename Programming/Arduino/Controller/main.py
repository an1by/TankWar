import serial, time
import tcpip
import config
import gcode
import re



# настройка соединения с дуней (Ардуино)
uart = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(1) #give the connection a second to settle

# Подключение к серверу
tcpip.connect_default()
tcpip.init()

# Сюда закидывается все что пишет дуня
file = open("uart.log", "w")

# Отправка команды. Конец строки \n добавляется 
def uart_write(command: str) -> None:
    uart.write(str.encode(command + "\n"))

uart_status: str = ""
uart_status_last = ""

coordinate = {}

def uart_read() -> None:
    """
    Принимает ответы с дуни, если состояние то меняет глобально
    """
    data = str(uart.readline())[2:-5]
    if data:
        
        # Если статус, то меняет его в глобале
        if re.fullmatch(r'<\S+>', data):
            global uart_status, uart_status_last
            row = data.strip()[1:-1].split('|')
            uart_status = row[0]
            if uart_status_last != uart_status:
                file.write(data + "\n")
                uart_status_last = uart_status

            global coordinate
            row = row[1][5:].split(',')
            coordinate['x'] = float(row[0])
            coordinate['y'] = float(row[1])
            coordinate['angle'] = float(row[2])
            # file.write(coordinate)
        else:
            if data == "ok":
                return
            file.write(data + "\n")

def ctrl_magnet(status: bool) -> None:
    """
    Вкл/Выкл магниты
    """
    file.write('Magnet {}'.format(status) + "\n")
    uart_write("M" + str(8 if status else 9))

def short_angle(angle: float):
    return angle if angle <= 180 else 180 - angle

# ------------------- MAIN --------------------------

uart_read()
# (G21 — выбор метрической системы единиц - миллиметры,)
# (G40 — отменяет автоматическую коррекцию на радиус инструмента.)
# (G49 — отменяет автоматическую коррекцию на длину инструмента.)
# (G53 — отменяет возможно введённые ранее дополнительные системы координат, смещённые относительно исходной и переводит станок в основную систему координат.)
# (G80 — отменяет все постоянные циклы, например, циклы сверления и их параметры.)
# (G90 — переводит в абсолютную систему координат.)
# (G17 — выбирается плоскость круговой интерполяции X-Y.)
uart_write("G21 G40 G49 G53 G90 G17")
uart_read()

ctrl_magnet(False)

command_to_last = {}
is_sended = True

# Основной цикл
while True:
    uart_write("?") # опрос состояния
    
    # Принимаем с дуни и в лог
    uart_read()

    # if not (uart_status in ["Idle", "Run"]):
        

        #uart.write(str.encode("$J=G21G91X10F100\n")) 
    # uart_write("?")
    # print(str(uart.readline()))
    command = {}

    # Принимаем команды от сервака
    for recived in tcpip.get_data():
        recived = {
            "action": "tank_move", 
            "from":{
                "x": 5,
                "y": 6,
                "angle": 180
            },
            "to":{
                "x": 6,
                "y": 6,
                "angle": 180
            }
        }
        if recived:
            print(recived)
            if recived['action'] == 'log_console':
                continue
            file.write(str(recived) + "\n")
            
            is_sended = False
            # json -> G-сode команды
            command_to_last = recived['to']
            # print(command_to_last)
            

            # Разные системы координат поэтому домножаем
            command["from"] = gcode.move(
                recived['from']['x'] * config.MULL,
                recived['from']['y'] * config.MULL
                )
            command["from_angle"] = gcode.rotate(
                short_angle(recived['from']['angle']) * config.MULL_ANGLE
            )
            command['rotate'] = gcode.rotate(
                gcode.angle(recived['to']['x'] - recived['from']['x'], recived['to']['y'] - recived['from']['y']) * config.MULL_ANGLE
            )
            command["to"]   = gcode.move(
                recived['to']['x'] * config.MULL,
                recived['to']['y'] * config.MULL
                )
            command["to_angle"] = gcode.rotate(
                short_angle(recived['to']['angle']) * config.MULL_ANGLE
            )

    if command:
        def exe_command(com, extra = ""):
            uart_write(command[com] + extra)
            del command[com]
        
        exe_command('from', config.F(100))
        exe_command('from_angle', config.F(20))
        
        ctrl_magnet(True)

        exe_command('rotate', config.F(20))
        # поворот перед тем как ехать


        exe_command('to', config.F(100))
        exe_command('to_angle', config.F(50))

        ctrl_magnet(False)
    
    print(command_to_last, coordinate)
    if not(is_sended) and command_to_last == coordinate:
        is_sended = True
        tcpip.send_data({"command": "ready_move"})
        file.write("ready_move")
        print("ready_move")
        #TODO: отправка готовности серваку



