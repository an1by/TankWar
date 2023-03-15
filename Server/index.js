require('dotenv').config()

require('./http_server.js')

const net = require('net');
const Logger = require("./logger.js");
const {createAddress, createPosition} = require("./utils");
let {Tank, getTank, getTankByPosition, tank_list, getTankByAddress} = require("./tank");
let {isObstacle, Obstacle, obstacle_list} = require("./obstacles");
const {Client, client_list, getClient} = require("./client")

let raspberry = undefined;

let pos_red = []
let pos_blue = []

const server = net.createServer(socket => {
    const address = createAddress(socket);
    Logger.info('Подключено устройство с IP: ' + address);
    socket.write('1', 'utf-8')
    socket.on('data', received => {
        let data = JSON.parse(received.toString());
        switch (data["command"]) {
            case "set_pos": {
                pos_red = data["red"]
                pos_blue = data["blue"]
                break
            }
            case "get": {
                socket.write(JSON.stringify({
                    "red": pos_red,
                    "blue": pos_blue
                }), 'utf-8')
                break
            }
            case "debug": {
                console.log(data["message"])
                break
            }
            case "clear": {
                raspberry = undefined;
                tank_list.forEach(tank => tank.disconnect())
                tank_list = []
                obstacle_list = []
                client_list.forEach(client => client.disconnect())
                Logger.success('Данные очищены, клиенты отключены!')
                break
            }
            case "init": {
                switch (data["who"]) {
                    case "tank": {
                        const number = data["number"];
                        new Tank(number, socket);
                        Logger.success(`Танк №${number} инициализирован. Адрес: ` + address)
                        break
                    }
                    case "raspberry": {
                        if (!raspberry) {
                            raspberry = socket
                            Logger.success(`Raspberry Pi инициализирована. Адрес: ` + address)
                        }
                        break
                    }
                    case "obstacle": {
                        if (raspberry.address !== address)
                            return;
                        const positions = data["positions"];
                        if (!positions[0] || !positions[1])
                            return;
                        new Obstacle(positions[0], positions[1]);
                        break
                    }
                    case "client": {
                        new Client(socket)
                        break
                    }
                }
                break
            }
            case "move": {
                if (address !== raspberry.address)
                    return;
                const number = data["number"],
                    position = data["position"]
                let tank = getTank(number);
                if (!tank)
                    return;
                if (position.x < 0 || position.y < 0) {
                    tank.disconnect();
                    Logger.warning(`Танк №${number} вышел за поле! Отключен.`)
                    return;
                }
                tank.position.x = position.x;
                tank.position.y = position.y;
                break
            }
            case "reload": {
                if (!getClient(address))
                    return;
                const number = data["number"]
                const tank = getTankByAddress(number);
                if (!tank) {
                    Logger.error(`Танк с адресом ${address} не найден!`)
                    return;
                }
                tank.reload()
                Logger.info(`Танк №${tank.number} перезарядился.`)
                break
            }
            case "aim": { // От клиента
                if (!getClient(address))
                    return;
                const number = data["number"],
                    target_position = createPosition(data[2]);
                const tank = getTank(number);
                if (!target_position || !tank) {
                    Logger.error(`При атаке со стороны танка №${number} произошла ошибка!`)
                    return;
                }
                const result = tank.aim(target_position)
                if (result)
                    Logger.info(`Производим прицеливание для танка №${number}. Координаты: ${target_position.x}:${target_position.y}`);
                else {
                    Logger.error(`Танк №${number} попытался прицелиться. Танк не заряжен!`)
                }
                // Танк принимает команду, поворачивает башню, производится звук выстрела, танк отправляет команду fire_bt серверу
                break
            }
            case "fire": { // От танка
                const tank = getTankByAddress(address);
                if (!tank) {
                    Logger.error(`Танк с адресом ${address} не найден!`)
                    return;
                }
                const result = tank.fire()
                Logger.info(`Танк №${tank.number} выстрелил! ${result}`)
                break
            }
        }
    });

    socket.on('end', () => {
        Logger.info('Устройство отключено. IP: ' + address)
        // if (raspberry && address === raspberry.address) {
        //     raspberry = {}
        //     return
        // }
        // let tank = getTankByAddress(address);
        // if (tank) {
        //     tank.delete()
        //     return;
        // }
    });
});

server.listen(process.env.PORT, function() {
    console.log(`Сервер запущен на порту: ${process.env.PORT}`);
});