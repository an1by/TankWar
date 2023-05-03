const {getObstacle} = require("./obstacles");
const {Client, getWithType} = require("./client")
const {getAngle, sleep} = require("./utils")
let tank_list = []

class Tank {
    constructor(number, team, socket) {
        this.client = new Client(socket, "tank")
        this.team = team
        this.number = number
        this.temp_target = {
            x: -1,
            y: -1
        }
        this.temp_move = {
            x: -1,
            y: -1,
            angle: -1
        }
        for (let tank of tank_list) {
            if (tank.number === number && tank.team == team) {
                this.position = tank.position
                this.dead = tank.dead
                return this;
            }
        }
        this.position = {
            x: 0,
            y: 0,
            angle: 0
        }
        this.dead = false
        tank_list.push(this)
        return this;
    }
    pre_move(position) {
        this.temp_move = {
            x: position["x"],
            y: position["y"],
            angle: position["angle"]
        }
        this.client.broadcast_data("controller", {
            "action": "move_tank",
            "from": this.position,
            "to": this.temp_move
        })
    }
    move() {
        if (this.temp_move.x !== -1) {
            this.position = this.temp_move
            this.temp_move = {
                x: -1,
                y: -1,
                angle: -1
            }
            return `(X: ${this.position.x} | Y: ${this.position.y} | Угол: ${this.position.angle})`;
        }
        return undefined;
    }
    disconnect() {
        if (this.client)
            this.client.disconnect();
        for (let i = 0; i < tank_list.length; i++) {
            let tank = tank_list[i]
            if (tank && tank.client.address === this.client.address) {
                tank_list.splice(i, 1);
            }
        }
        return true
    }
    pre_fire(target_position) {
        this.temp_target = target_position
        let new_pos = this.position;
        new_pos.angle = getAngle(this.position, target_position);
        this.client.broadcast_data("controller", {
            "action": "move_tank",
            "from": this.position,
            "to": new_pos
        })
    }
    fire() {
        this.client.send_data({
            action: "fire"
        })
        sleep(1000);
        let target_position = this.temp_target;
        this.temp_target = {
            x: -1,
            y: -1
        }
        const target = getTankByPosition(target_position)
        if (!target) {
            // this.socket.write('miss')
            return {
                "action": "fire_feedback",
                "object": {
                    "name": "none",
                    "position": target_position
                },
                "message": `(Не найдена цель, выстрел в пустоту)`
            }
        }
        const multiplier = target.position.x / target.position.y;
        for (let i = 0; i <= target.position.x; i += 0.1) {
            let x = this.position.x + i;
            let y = this.position.y + i / multiplier;
            const obstacle = getObstacle({x: x, y: y})
            if (obstacle) {
                // this.socket.write('miss')
                return {
                    "action": "fire_feedback",
                    "object": {
                        "name": "obstacle",
                        "position": obstacle.position
                    },
                    "message": `(Пуля попала в препятствие)`
                }
            }
        }
        // this.socket.write('target_killed')
        target.dead = true;
        // target.socket.write('dead');
        target.client.send_data({action: "status", life: false})
        return {
            "action": "fire_feedback",
            "object": {
                "name": "tank",
                "number": target.number,
                "team": target.team
            },
            "message": `(Уничтожен танк №${target.number})`
        }
    }
}

function getTank(number, team) {
    for (let tank of tank_list) {
        if (tank.number === number && tank.team == team)
            return tank
    }
    return undefined
}

function getTankByAddress(address) {
    for (let tank of tank_list) {
        if (tank.client.address === address)
            return tank
    }
    return undefined
}

function getTankByPosition(position) {
    return tank_list.find(tank =>
        tank.position.x === position.x
        &&
        tank.position.y === position.y
    );
}

function getTanks() {
    let tanks = []
    for (let tank of tank_list) {
        tanks.push({
            team: tank.team,
            number: tank.number,
            position: tank.position,
            dead: tank.dead
        })
    }
    return tanks
}

module.exports = {
    Tank, tank_list, getTank, getTankByAddress, getTankByPosition, getTanks
}