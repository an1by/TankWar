const {getWithType} = require("./client")
const Logger = require("./logger.js");
const { getTanks, Tank, tank_list } = require("./tank");
const { getObstacles, Obstacle, obstacles_list } = require("./obstacles")

let step_timer = -10;
let pause = false;

async function start_game() {
    //////TO DELETE//////
    for (let i = 0; i < 6; i++) {
        let team = (i > 2 ? "red" : "blue")
        let number = i
        if (number > 2) 
            number -= 3
        const t = new Tank(number, team, undefined)
        t.position.x = i;
        t.position.y = (team == "red" ? 0 : 7)
        t.position.angle = (team == "red" ? 270 : 90)
    }
    //////TO DELETE//////
    new Obstacle("river", 2, 3);
    new Obstacle("river", 2, 4);
    new Obstacle("river", 3, 5);
    new Obstacle("river", 4, 6);
    new Obstacle("full", 5, 4);
    new Obstacle("full", 5, 5);
    new Obstacle("full", 4, 5);
    //////TO DELETE//////
    step_timer = 30
    await start_timer()
    for (let client of getWithType("client")) {
        client.step = (client.team == "red")
        client.send_data({
            "action": "set_tanks",
            "tanks": getTanks()
        })
        client.send_data({
            "action": "set_obstacles",
            "obstacles": getObstacles()
        })
    }
    Logger.success('Игра успешно запущена!')
}

function end_game() {
    tank_list.forEach(tank => tank.disconnect())
    obstacles_list.forEach(obstacle => obstacle.delete())
    ////////////////////
    step_timer = -10
    for (let client of getWithType("client")) {
        client.step = "none"
        client.send_data({
            "action": "step_feedback",
            "time": -10,
            "step": "none"
        })
    }
    Logger.success('Игра успещно завершена!')
}

function pause_game(status) {
    pause = status
    if (pause)
        change_step("pause")
    else {
        step_timer = -1
        change_step("nonpause")
    }
}

function change_step(step) {
    for (let client of getWithType("client")) {
        switch (step) {
            case "pause":
                client.step = client.step.toString() + '_pause'
                break
            case "nonpause":
                console.log(client.step === 'true_pause')
                client.step = (client.step === 'true_pause')
                break
            default:
                if (step)
                    client.step = step
                break
        }
    }
}

function send_time(change_step=false) {
    if (getWithType("client").length !== 2) {
        end_game()
        return
    }
    if (change_step)
        step_timer = 30
    for (let client of getWithType("client")) {
        if (change_step) {
            switch (client.step) {
                case true | false:
                    client.step = !client.step
            }
        }
        client.send_data({
            "action": "step_feedback",
            "time": step_timer,
            "step": client.step
        })
    }
}

async function start_timer() {
    let id = setInterval(() => {
        if (!pause) {
            if (step_timer > 0) {
                step_timer -= 1
                send_time()
            } else if (step_timer <= -10) {
                end_game()
                clearInterval(id)
                return
            } else {
                send_time(true)
            }
        }
    }, 1000)
}

module.exports = {
    start_timer, start_game, end_game, send_time, pause_game
}