let obstacles_list = []

class Obstacle {
    constructor(type, x, y) {
        this.position = {
            x: x,
            y: y
        }
        this.type = type
        obstacles_list.push(this)
    }
    delete() {
        for (let i = 0; i < obstacles_list.length; i++){
            if (obstacles_list[i].position === this.position) {
                obstacles_list.splice(i, 1)
                return true;
            }
        }
        return false;
    }
}

function getObstacles() {
    let obstacles = []
    for (let obstacle of obstacles_list) {
        obstacles.push({
            "position": obstacle.position,
            "type": obstacle.type
        })
    }
    return obstacles
}

function getObstacle(position) {
    for (let obstacle of obstacles_list) {
        if (obstacle.position.x == position["x"] && obstacle.position.y == position["y"])
            return obstacle;
    }
    return undefined;
}

module.exports = {
    Obstacle, obstacles_list, getObstacle, getObstacles
}