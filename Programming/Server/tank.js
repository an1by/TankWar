const {getObstacle} = require("./obstacles");
const {Client} = require("./client")
let tank_list = []

class Tank {
    constructor(number, team, socket) {
        this.client = new Client(socket, "tank")
        this.team = team
        this.number = number
        for (let tank of tank_list) {
            if (tank.number === number) {
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
    move(position) {
        this.position.x = position.x
        this.position.y = position.y
    }
    disconnect() {
        if (!this.client)
            return true
        this.client.disconnect();
        return true
    }
    fire(target_position) {
        const target = getTankByPosition(target_position)
        if (!target) {
            // this.socket.write('miss')
            return {
                "action": "fire_feedback",
                "object": {
                    "name": "none"
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
        return {
            "action": "fire_feedback",
            "object": {
                "name": "tank",
                "number": target.number,
                "position": target.position
            },
            "message": `(Уничтожен танк №${target.number})`
        }
    }
}

function getTank(number) {
    for (let tank of tank_list) {
        if (tank.number === number)
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