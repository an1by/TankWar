require('dotenv').config()

// require('./http_server.js')

const net = require('net');
const Logger = require("./logger.js");
const {createAddress, createPosition, arrayToPosition, getAngle} = require("./utils.js");
let {Tank, getTank, getTankByPosition, tank_list, getTankByAddress} = require("./tank.js");
let {isObstacle, Obstacle, obstacles_list, getObstacle} = require("./obstacles.js");
let {Client, client_list, getClient, getWithType, countClientType} = require("./client.js")
let {start_game, send_time, pause_game, pause} = require("./game_controller.js")

let raspberry = undefined;

Logger.info('Танков инициализировано: ' + tank_list.length);

const server = net.createServer(async (socket) => {
    const address = createAddress(socket);

    Logger.info('Подключено устройство с IP: ' + address);
    try {
        socket.write(JSON.stringify({"action": "log_console", "message": "Вы подключены к серверу!"}), 'utf-8');
    } catch (e) {
        //
    }
    let client = undefined
    socket.on('data', async (received) => {
        try {
            let recv = received.toString();
            let data = JSON.parse(recv);
            console.log(data)
            switch (data["command"]) {
                case "ready_move": {
                    break
                }
                case "log": {
                    console.log(data["message"])
                    break
                }
                case "get": {
                    switch (data["what"]) {
                        case "obstacles":
                            return obstacles_list
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
                            obstacles_list = []
                            client_list.forEach(client => client.disconnect())
                            Logger.success('Данные очищены, клиенты отключены!')
                            break
                        case "obstacles":
                            obstacles_list = []
                            break
                    }
                    break
                }
                case "edit": {
                    switch (data["what"]) {
                        case "obstacles": {
                            data["list"].forEach(obs => {
                                if (obs["positions"] && positions[0] && positions[1] && obs["type"]) {
                                    const positions = obs["positions"]
                                    const type = obs["type"]
                                    let obstacle = getObstacleWithArray(positions);
                                    
                                    if (obstacle) {
                                        if (type == "empty")
                                            obstacle.delete();
                                        else 
                                            obstacle.type = type;
                                    }
                                    else new Obstacle(type, positions[0], positions[1]);
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
                                client = new Client(socket, data["who"])
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
                        default: {
                            client = new Client(socket, data["who"])
                            break
                        }
                    }
                    break
                }
                case "step": {
                    switch (data["what"]) {
                        case "move": {
                            if (!client || client.type !== "client")
                                return
                            const number = data["number"],
                                position = data["position"]
                            let tank = getTank(number, client.team);
                            if (!tank)
                                return;
                            if (position.x < 0 || position.y < 0) {
                                tank.disconnect();
                                Logger.warning(`Танк №${number} вышел за поле! Отключен.`)
                                return;
                            }
                            client.broadcast_data("controller", {
                                "action": "move_tank",
                                "from": tank.position,
                                "to": position
                            })
                            tank.move(position)
                            client.broadcast_data("client", {
                                "action": "move_tank",
                                "team": client.team,
                                "number": tank.number,
                                "position": position
                            })
                            send_time(true)
                            break
                        }
                        case "fire": { // От клиента
                            if (!client || client.type !== "client")
                                return
                            const number = data["number"],
                                target_position = data["position"]
                            const tank = getTank(number, client.team);
                            if (!tank) {
                                Logger.error(`Танк с номером ${number} не найден!`)
                                return;
                            }
                            tank.pre_fire(target_position)
                        }
                        case "final_fire": {
                            if (!client || client.type !== "controller")
                                return
                            let result = undefined,
                                tank = undefined;
                            for (let d_tank of tank_list) {
                                if (d_tank.temp_target.x !== -1) {
                                    result = d_tank.fire()
                                    tank = d_tank
                                    break
                                }
                            }
                            if (result && tank) {
                                Logger.info(`Танк №${tank.number} из команды ${tank.team} выстрелил! ${result.message}`)
                                client.send_data(result)
                                client.broadcast_data("client", result)
                                send_time(true)
                                pause_game(false)
                            } else {
                                Logger.error(`Танк с предварительной целью для атаки не найден!`)
                            }
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
        if (client) {
            client.disconnect()
        }
        Logger.info('Устройство отключено произвольно или вследствие ошибки. IP: ' + address)
    });

    socket.on('end', () => {
        if (client) {
            client.disconnect()
        }
        Logger.info('Устройство отключено. IP: ' + address)
    });
});

server.listen(process.env.PORT, function() {
    console.log(`Сервер запущен на порту: ${process.env.PORT}`);
});