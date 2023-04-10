const {getWithType} = require("./client")
const Logger = require("./logger.js");

let step_timer = 30

async function start_game() {
    step_timer = 30
    await start_timer()
    for (let client of getWithType("client")) {
        client.step = (client.team == "red")
    }
    Logger.success('Игра успешно запущена!')
}

function end_game() {
    for (let client of getWithType("client")) {
        client.step = "none"
    }
}

function send_time(change_step) {
    for (let client of getWithType("client")) {
        if (change_step)
            client.step = client.step == "none" ? "none" : !client.step
        client.send_data({
            "action": "step_feedback",
            "time": step_timer,
            "step": client.step
        })
    }
}

async function start_timer() {
    setInterval(() => {
        if (step_timer > 0) {
            step_timer -= 1
            send_time(false)
        } else {
            step_timer = 30
            send_time(true)
        }
    }, 1000)
}

module.exports = {
    start_timer, start_game, end_game
}