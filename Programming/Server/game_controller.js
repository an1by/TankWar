const {getWithType} = require("./client")
const Logger = require("./logger.js");
const { getTanks } = require("./tank");

let step_timer = -10

async function start_game() {
    step_timer = 30
    await start_timer()
    for (let client of getWithType("client")) {
        client.step = (client.team == "red")
        client.send_data({
            "action": "set_tanks",
            "tanks": getTanks()
        })
    }
    Logger.success('Игра успешно запущена!')
}


function end_game() {
    step_timer = -10
    for (let client of getWithType("client")) {
        client.step = "none"
        client.send_data({
            "action": "step_feedback",
            "time": -10,
            "step": "none"
        })
    }
}

function send_time(change_step) {
    let clients = getWithType("client")
    if (clients.length !== 2) {
        end_game()
        return
    }
    for (let client of clients) {
        if (change_step) {
            client.step = client.step === "none" ? "none" : !client.step
            step_timer = 30
        }
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
        } else if (step_timer == -10) {
            end_game()
        } else {
            step_timer = 30
            send_time(true)
        }
    }, 1000)
}

module.exports = {
    start_timer, start_game, end_game, send_time
}