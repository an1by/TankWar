require('dotenv').config()

// require('./http_server.js')

const net = require('net');
const Logger = require("./logger.js");
const {createAddress, createPosition, arrayToPosition} = require("./utils");
let {Tank, getTank, getTankByPosition, tank_list, getTankByAddress} = require("./tank");
let {isObstacle, Obstacle, obstacle_list, getObstacle} = require("./obstacles");
const {Client, client_list, getClient, getWithType} = require("./client")

let raspberry = undefined;

let pos_red = []
let pos_blue = []

for (let i = 0; i < 6; i++) {
    const t = new Tank(i+1, i >= 3 ? "blue" : "red", undefined)
    t.position.x = i;
    t.position.y = i;
}

const server = net.createServer(socket => {
    const address = createAddress(socket);

    Logger.info('Подключено устройство с IP: ' + address);
    try {
        socket.write(JSON.stringify({"action": "log_console", "message": "Вы подключены к серверу!"}), 'utf-8');
    } catch (e) {
        console.error(e)
    }

    socket.on('data', received => {
        try {
            let data = JSON.parse(received.toString());
            // console.log(received.toString())
            switch (data["command"]) {
                case "log": {
                    console.log(data["message"])
                }
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
                    switch (data["what"]) {
                        case "all":
                            raspberry = undefined;
                            tank_list.forEach(tank => tank.disconnect())
                            tank_list = []
                            obstacle_list = []
                            client_list.forEach(client => client.disconnect())
                            Logger.success('Данные очищены, клиенты отключены!')
                            break
                        case "obstacles":
                            obstacle_list = []
                            break
                    }
                }
                case "edit": {
                    switch (data["what"]) {
                        case "obstacles": {
                            data["list"].forEach(obs => {
                                const positions = obs["positions"]
                                const state = obs["state"]
                                if (positions[0] && positions[1] && obs["state"]) {
                                    let obstacle = getObstacleWithArray(positions);
    
                                    if (obstacle) {
                                        if (state == "empty")
                                            obstacle.delete();
                                        else 
                                            obstacle.state = state;
                                    }
                                    else new Obstacle(obs[type], positions[0], positions[1]);
                                }
                            });
                        }
                    }
                }
                case "init": {
                    switch (data["who"]) {
                        case "tank": {
                            if (getWithType("tank").length >= 6)
                                return
                            const number = data["number"];
                            new Tank(number, (number < 3 ? "red" : "blue"), socket);
                            Logger.success(`Танк №${number} инициализирован. Адрес: ` + address)
                            break
                        }
                        case "obstacle": {
                            // if (raspberry.address !== address)
                            //     return;
                            const positions = data["positions"];
                            if (!positions[0] || !positions[1])
                                return;
                            new Obstacle(positions[0], positions[1]);
                            break
                        }
                        default: {
                            if (!getWithType(data["who"])) {
                                new Client(socket, data["who"])
                                Logger.success(`Клиент ${data["who"]} инициализирован. Адрес: ` + address)
                            }
                            break
                        }
                    }
                    break
                }
                case "move": {
                    // if (address !== raspberry.address)
                    //     return;
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
                case "fire": { // От танка
                    const tank = getTank(data["number"]);
                    const target_position = data["position"]
                    if (!tank) {
                        Logger.error(`Танк с номером ${data["number"]} не найден!`)
                        return;
                    }
                    const result = tank.fire(target_position)
                    Logger.info(`Танк №${tank.number} выстрелил! ${result.message}`)
                    socket.write(JSON.stringify(result), 'utf-8') // fire_feedback
                    break
                }
            }
        } catch (e) {
            console.error(e)
        }
    });

    socket.on('end', () => {
        Logger.info('Устройство отключено. IP: ' + address)
    });
});

server.listen(process.env.PORT, function() {
    console.log(`Сервер запущен на порту: ${process.env.PORT}`);
});