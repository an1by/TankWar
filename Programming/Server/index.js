require('dotenv').config()

// require('./http_server.js')

const net = require('net');
const Logger = require("./logger.js");
const {createAddress} = require("./utils.js");
let {Tank, getTank, tank_list, getTanks} = require("./tank.js");
let {Obstacle, obstacles_list, getObstacle, getObstacles} = require("./obstacles.js");
let {Client, client_list, getWithType} = require("./client.js")
let {start_game, pause_game, send_time, end_game, send_field_setup, step_timer} = require("./game_controller.js");
// const { setUrl } = require('./http_server.js');

let raspberry = undefined;

// let game = new GameController()

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
            switch (data["command"]) {
                case "log": {
                    console.log(data["message"])
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
                        case "tanks":
                            tank_list.forEach(tank => tank.disconnect())
                            tank_list = []
                            break
                        case "tank":
                            const number = data["number"],
                                team = data["team"]
                            let tank = getTank(number, team);
                            if (tank) {
                                tank.disconnect()
                                client.broadcast_data("client", {
                                    "action": "set_tanks",
                                    "tanks": getTanks()
                                })
                                client.send_data({
                                    "action": "set_tanks",
                                    "tanks": getTanks()
                                })
                            }
                            break
                    }
                    break
                }
                case "edit": {
                    switch (data["what"]) {
                        case "obstacles": {
                            data["list"].forEach(obs => {
                                if (obs["position"] && obs["type"]) {
                                    const position = obs["position"]
                                    const type = obs["type"]
                                    let obstacle = getObstacle(position);

                                    if (obstacle) {
                                        if (type == "empty")
                                            obstacle.delete();
                                        else 
                                            obstacle.type = type;
                                    }
                                    else new Obstacle(type, position["x"], position["y"]);
                                }
                            });
                            client.broadcast_data("client", {
                                "action": "set_obstacles",
                                "obstacles": getObstacles()
                            })
                            break
                        }
                    }
                    break
                }
                case "init": {
                    switch (data["who"]) {
                        case "tank": {
                            if (getWithType("tank").length >= 6)
                                return
                            const number = data["number"],
                                team = data["team"] // red/blue
                            let new_tank = getTank(number, team);
                            if (new_tank) {
                                Logger.error(`Произошла ошибка при обработке танка №${number} из команды ${team}! Уже инициализирован. (IP: ${address})`)
                                return
                            }

                            new_tank = new Tank(number, team)
                            Logger.success(`Новый танк №${number} команды ${team} инициализирован.`)

                            if ("move" in data && "x" in data["move"] && "y" in data["move"] && "angle" in data["move"]) {
                                position = {
                                    x: data["move"]["x"],
                                    y: data["move"]["y"],
                                    angle: data["move"]["angle"]
                                }
                                new_tank.pre_move(position, false)
                                new_tank.move()
                                new_tank.move_send()
                            }
                            client.broadcast_data("client", {
                                "action": "set_tanks",
                                "tanks": getTanks()
                            })
                            getWithType("manager").forEach(manager =>
                                manager.send_data({
                                    "action": "set_tanks",
                                    "tanks": getTanks()
                                })    
                            )
                            
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
                            let counter = getWithType("client").length
                            if (counter < 2) {
                                client = new Client(socket, "client")
                                counter += 1
                                Logger.success(`${data["who"]} №${counter} инициализирован. Адрес: ` + address)
                                team = (counter === 1 ? "blue" : "red")
                                client.team = team
                                client.send_data({"action": "init", "team": team})
                                if (counter == 2) {
                                    await start_game()
                                }
                            }
                            break
                        }
                        case "manager":
                            if (getWithType("manager").length > 0)
                                return
                            client = new Client(socket, "manager")
                            send_field_setup("manager")
                            break
                        default: {
                            client = new Client(socket, data["who"])
                            break
                        }
                    }
                    break
                }
                case "step": {
                    switch (data["what"]) {
                        case "skip":
                            send_time(true)
                            break
                        case "dead_status": {
                            const number = data["number"],
                                team = data["team"]
                            let tank = getTank(number, team);
                            if (!tank)
                                return;
                            tank.dead = data["status"]
                            client.broadcast_data("client", {
                                "action": "fire_feedback",
                                "object": {
                                    "name": "tank",
                                    "number": number,
                                    "team": team
                                },
                                "message": `(Уничтожен танк №${number})`
                            })
                            break
                        }
                        case "move_anyway":
                            if (client.type !== "manager")
                                return
                            const number = data["number"],
                                position = data["position"],
                                team = data["team"]
                            let tank = getTank(number, team);
                            if (!tank)
                                return;
                            if (position.x < 0 || position.y < 0) {
                                tank.disconnect();
                                Logger.warning(`Танк №${number} вышел за поле! Отключен.`)
                                return;
                            }
                            tank.pre_move(position, false)
                            let result = tank.move()
                            tank.move_send()
                            Logger.info(`Танк №${number} из команды ${team} передвинут менеджером! ${result}`)
                            break
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
                            let thereController = tank.pre_move(position)
                            pause_game(true)
                            if (thereController) {
                                break
                            }
                        }
                        case "final_move": {
                            let result = undefined,
                                tank = undefined;
                            for (let d_tank of tank_list) {
                                if (d_tank.temp_move.x !== -1) {
                                    result = d_tank.move()
                                    tank = d_tank
                                    break
                                }
                            }
                            if (result !== undefined && tank !== undefined) {
                                Logger.info(`Танк №${tank.number} из команды ${tank.team} передвинут! ${result}`)
                                tank.move_send(true)
                                pause_game(false)
                            } else {
                                Logger.error(`Танк с предварительной позицией для передвижения не найден!`)
                            }
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
                            pause_game(true)
                            if (getWithType("controller").length > 0) {
                                break
                            }
                        }
                        case "final_fire": {
                            // if (!client || client.type !== "controller")
                            //     return
                            let result = undefined,
                                tank = undefined;
                            for (let d_tank of tank_list) {
                                if (d_tank.temp_target.x !== -1) {
                                    result = d_tank.fire()
                                    tank = d_tank
                                    break
                                }
                            }
                            if (result !== undefined && tank !== undefined) {
                                Logger.info(`Танк №${tank.number} из команды ${tank.team} выстрелил! ${result.message}`)
                                if (client.type !== "controller")
                                    client.send_data(result)
                                client.broadcast_data("client", result)
                                client.broadcast_data("manager", result) //MANAGER
                                pause_game(false)

                                let dead_counter = [0, 0]
                                let all_counter = [0, 0]
                                tank_list.forEach((tank) => {
                                    all_counter[(tank.team == "red") ? 0 : 1] += 1
                                    if (tank.dead)
                                        dead_counter[(tank.team == "red") ? 0 : 1] += 1
                                })
                                if (dead_counter[0] == all_counter[0])
                                    end_game("blue")
                                else if (dead_counter[1] == all_counter[1])
                                    end_game("red")
                            } else {
                                Logger.error(`Танк с предварительной целью для атаки не найден!`)
                            }
                            break
                        }
                    }
                }
            }
        } catch (e) {
            Logger.error(`Ошибка выполнения кода со стороны ${address}: ${e.message}`)
            Logger.error(e)
        }
    });

    socket.on('error', function(ex) {
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
    Logger.info(`Сервер запущен на порту: ${process.env.PORT}`);
});