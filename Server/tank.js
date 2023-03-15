const {createAddress} = require("./utils");
const {isObstacle} = require("./obstacles");
let tank_list = []

class Tank {
    constructor(number, team, socket) {
        this.number = number
        this.socket = socket
        this.team = team
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
    disconnect() {
        if (!this.socket)
            return true
        this.socket.write('disconnect', 'utf-8');
        this.socket = undefined
        return true
    }
    address() {
        createAddress(this.socket)
    }
    fire(target_position) {
        const target = getTankByPosition(target_position)
        if (!target) {
            this.socket.write('miss')
            return {
                "object": "none",
                "message": `(Не найдена цель, выстрел в пустоту)`
            }
        }
        const multiplier = target.position.x / target.position.y;
        for (let i = 0; i <= target.position.x; i += 0.1) {
            let x = this.position.x + i;
            let y = this.position.y + i / multiplier;
            if (isObstacle({x: x, y: y})) {
                this.socket.write('miss')
                return {
                    "object": "obstacle",
                    "message": `(Пуля попала в препятствие)`
                }
            }
        }
        this.socket.write('target_killed')
        target.dead = true;
        target.socket.write('dead');
        return {
            "object": "tank",
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
        if (tank.address() === address)
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

module.exports = {
    Tank, tank_list, getTank, getTankByAddress, getTankByPosition
}