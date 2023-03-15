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
                this.charged = tank.charged
                this.target = tank.target
                this.dead = tank.dead
                return this;
            }
        }
        this.position = {
            x: 0,
            y: 0,
            angle: 0
        }
        this.charged = true
        this.target = {} // Target Position
        this.dead = false
        tank_list.push(this)
        return this;
    }
    disconnect() {
        this.socket.write('disconnect', 'utf-8');
        this.socket = undefined
        return false
    }
    address() {
        createAddress(this.socket)
    }
    reload() {
        if (this.charged)
            return false;
        this.charged = true;
        this.socket.write('reload', 'utf-8')
        return true;
    }
    aim(target_position) {
        if (!this.charged)
            return false;
        this.socket.write('aim:' + target_position.angle);
        this.target = target_position
        return true;
    }
    fire() {
        this.charged = false;
        const target = getTankByPosition(this.target)
        if (!target) {
            this.socket.write('miss')
            return `(Не найдена цель, выстрел в пустоту)`;
        }
        const multiplier = target.position.x / target.position.y;
        for (let i = 0; i <= target.position.x; i += 0.1) {
            let x = this.position.x + i;
            let y = this.position.y + i / multiplier;
            if (isObstacle({x: x, y: y})) {
                this.socket.write('miss')
                return `(Пуля попала в препятствие)`;
            }
        }
        this.socket.write('target_killed')
        target.dead = true;
        target.socket.write('dead');
        return `(Уничтожен танк №${target.number})`
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