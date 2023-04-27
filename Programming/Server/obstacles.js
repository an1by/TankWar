let obstacle_list = []

class Obstacle {
    constructor(type, x, y) {
        this.position = {
            x: x,
            y: y
        }
        this.type = type
        obstacle_list.push(this)
    }
    delete() {
        for (let i = 0; i < obstacle_list.length; i++){
            if (obstacle_list[i].position === this.position) {
                obstacle_list.splice(i, 1)
                return true;
            }
        }
        return false;
    }
}

function getObstacles() {
    let obstacles = []
    for (let obstacle of obstacle_list) {
        obstacles.push({
            "position": obstacle.position,
            "type": type
        })
    }
    return obstacles
}

function getObstacle(position) {
    for (let obstacle of obstacle_list) {
        if (obstacle.position.x == position.x && obstacle.position.y == position.y)
            return obstacle;
    }
    return undefined;
}

module.exports = {
    Obstacle, obstacle_list, getObstacle, getObstacles
}