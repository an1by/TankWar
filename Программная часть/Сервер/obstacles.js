let obstacle_list = []

class Obstacle {
    constructor(state, first_position, second_position) {
        this.position = [first_position, second_position]
        this.state = state
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

function getObstacle(position) {
    for (let obstacle of obstacle_list) {
        if (obstacle.position[0].x <= position.x <= obstacle.position[1].x && obstacle.position[0].y <= position.y <= obstacle.position[1].y)
            return obstacle;
    }
    return undefined;
}

function getObstacleWithArray(position_array) {
    for (let obstacle of obstacle_list) {
        if (obstacle.position[0].x == position_array[0][0] &&
            obstacle.position[0].y == position_array[0][1] &&
            obstacle.position[1].x == position_array[1][0] &&
            obstacle.position[1].y == position_array[1][1]
        ) {
            return obstacle;
        }
    }
    return undefined;
}

module.exports = {
    Obstacle, obstacle_list, getObstacle
}