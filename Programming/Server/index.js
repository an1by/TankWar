require('dotenv').config()

// require('./http_server.js')

const net = require('net');
const Logger = require("./logger.js");
const {createAddress, createPosition, arrayToPosition} = require("./utils.js");
let {Tank, getTank, getTankByPosition, tank_list, getTankByAddress} = require("./tank.js");
let {isObstacle, Obstacle, obstacle_list, getObstacle} = require("./obstacles.js");
let {Client, client_list, getClient, getWithType, countClientType} = require("./client.js")
let {start_game} = require("./game_controller.js")

let raspberry = undefined;

for (let i = 0; i < 6; i++) {
    const t = new Tank(i+1, i >= 3 ? "blue" : "red", undefined)
    t.position.x = i;
    t.position.y = i;
}

const server = net.createServer(async (socket) => {
    const address = createAddress(socket);

    Logger.info('Подключено устройство с IP: ' + address);
    try {
        socket.write(JSON.stringify({"action": "log_console", "message": "Вы подключены к серверу!"}), 'utf-8');
    } catch (e) {
        //
    }

    for (let i = 1; i <= 6; i++) {
        let new_tank = new Tank(i, (i < 4 ? "red" : "blue"), undefined);
        if (data["move"]) {
            position = {
                x: (i + 1),
                y: (i < 4 ? 7 : 0)
            }
            new_tank.move(position)
        }
    }
    Logger.info('Танков инициализировано: ' + tank_list.length)

    socket.on('data', async (received) => {
        try {
            let recv = received.toString();
            let data = JSON.parse(recv);
            switch (data["command"]) {
                case "log": {
                    console.log(data["message"])
                }
                case "get": {
                    switch (data["what"]) {
                        case "obstacles":
                            return obstacle_list
                        case "tanks":
                            return tank_list
                    }
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
                    break
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
                    break
                }
                case "init": {
                    switch (data["who"]) {
                        case "tank": {
                            if (getWithType("tank").length >= 6)
                                return
                            const number = data["number"];
                            const team = data["team"] // red/blue
                            let new_tank = new Tank(number, team, socket);
                            if (data["move"]) {
                                position = {
                                    x: data["move"]["x"],
                                    y: data["move"]["y"]
                                }
                                new_tank.move(position)
                            }
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
                        case "client": {
                            let counter = countClientType("client")
                            if (counter < 2) {
                                let client = new Client(socket, data["who"])
                                Logger.success(`${data["who"]} №${counter} инициализирован. Адрес: ` + address)
                                counter += 1
                                team = (counter === 1 ? "blue" : "red")
                                client.team = team
                                client.send_data({"action": "init", "team": team})
                                if (counter == 2) {
                                    await start_game()
                                }
                            }
                            break
                        }
                    }
                    break
                }
                case "step": {
                    switch (data["what"]) {
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
                            tank.move(position)
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
                }
            }
        } catch (e) {
            Logger.error('Ошибка выполнения кода: ' + e.message)
        }
    });

    socket.on('error', function(ex) {
        // console.log(ex)
        // ignore
    });
      

    socket.on('end', () => {
        for (let instance of [getClient(address), getTank(address)]) {
            if (instance) {
                instance.disconnect()
                break
            }
        }
        Logger.info('Устройство отключено. IP: ' + address)
    });
});

server.listen(process.env.PORT, function() {
    console.log(`Сервер запущен на порту: ${process.env.PORT}`);
});