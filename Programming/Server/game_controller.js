const {client_list} = require("./client")

let step_timer = 30

function start_game() {
    step_timer = 30
    for (let i = 0; i < client_list.length; i++) {
        let client = client_list[i]
        client.step = (i == 0)
        client.send_data({
            "action": "step_feedback",
            "time": step_timer,
            "step": client.step
        })
    }
    Logger.success('Игра успешно запущена!')
}

function end_game() {
    client_list.forEach((client) => {
        client.step = "none"
    })
}

function send_time(change_step) {
    client_list.forEach((client) => {
        if (change_step)
            client.step = client.step == "none" ? "none" : !client.step
        client.send_data({
            "action": "step_feedback",
            "time": step_timer,
            "step": client.step
        })
    })
}

async function start_timer() {
    setInterval(() => {
        if (timer > 0) {
            timer -= 1
            send_time(false)
        } else {
            timer = 30
            send_time(true)
        }
    }, 1000)
}

module.exprots = {
    start_timer, start_game, end_game
}