const {getWithType} = require("./client")
const Logger = require("./logger.js");
const { getTanks, Tank, tank_list } = require("./tank");
const { getObstacles, obstacles_list } = require("./obstacles");

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
        t.position.y = (team == "red" ? 0 : 1)
        t.position.angle = (team == "red" ? 270 : 90)
    }
    //////TO DELETE//////
    send_field_setup("client")
    send_field_setup("manager")
    step_timer = 30
    await start_timer()
    Logger.success('Игра успешно запущена!')
}

function send_field_setup(who) {
    for (const client of getWithType(who)) {
        if (who == "client")
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
}

function end_game(winner=undefined) {
    tank_list.forEach(tank => tank.disconnect())
    obstacles_list.forEach(obstacle => obstacle.delete())
    ////////////////////
    step_timer = -10
    for (const client of getWithType("client")) {
        client.step = "none"
        let json = {
            "action": "step_feedback",
            "time": -10,
            "step": "none"
        }
        if (winner)
            json["winner"] = winner
        client.send_data(json)
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
    for (const client of getWithType("client")) {
        switch (step) {
            case "pause":
                client.send_data({
                    "action": "switch_pause",
                    "pause": true
                })
                break
            case "nonpause":
                client.send_data({
                    "action": "switch_pause",
                    "pause": false
                })
                break
            default:
                if (step)
                    client.step = step
                    client.send_data({
                        "action": "step_feedback",
                        "time": step_timer,
                        "step": step
                    })
                break
        }
    }
}

function send_time(change_step=false) {
    if (getWithType("client").length !== 2) {
        step_timer = -10
        return
    }
    if (change_step)
        step_timer = 30
    for (const client of getWithType("client")) {
        if (change_step) {
            // console.log(client.step)
            switch (client.step) {
                case true:
                case false:
                    client.step = !client.step
            }
            // console.log(client.step)
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
        if (pause) {
            send_time()
        } else if (step_timer > 0) {
            step_timer -= 1
            send_time()
        } else if (step_timer <= -10) {
            end_game()
            clearInterval(id)
            return
        } else {
            send_time(true)
        }
    }, 1000)
}

module.exports = {
    start_timer, start_game, end_game, send_time, pause_game, send_field_setup, step_timer
}