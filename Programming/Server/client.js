const Logger = require("./logger");
const {createAddress} = require("./utils");
let client_list = []

class Client {
    constructor(socket, type) {
        this.socket = socket
        this.type = type
        this.address = createAddress(this.socket)
        this.step = true // true / false
        this.team = undefined
        client_list.push(this)
    }
    disconnect() {
        for (let i = 0; i < client_list.length; i++) {
            let client = client_list[i]
            if (client && client.address === this.address) {
                if (client.socket && !client.socket.destroyed)
                    try {
                        client.socket.write(JSON.stringify({"command": "disconnect"}))
                    } catch (exception) {
                        Logger.warning(`Клиент ${this.address} отключен произвольно!`)
                    }
                client_list.splice(i, 1);
            }
        }
    }
    send_data(data) {
        if (this.socket) {
            this.socket.write(JSON.stringify(data), 'utf-8');
            return true
        }
        return false
    }
    broadcast_data(who, data) {
        let k = 0
        for (let client of getWithType(who)) {
            if (client.socket) {
                k += 1
                client.send_data(data)
            }
        }
        return k > 0
    }
}

function getWithType(type) {
    let array = []
    for (let client of client_list) {
        if (client.type === type)
            array.push(client)
    }
    return array;
}

function getClient(address) {
    for (let client of client_list) {
        if (client.address === address)
            return client;
    }
    return undefined;
}

// function countClientType(type) {
//     let amount = 0
//     for (let client of client_list) {
//         if (client.type === type)
//             amount += 1
//     }
//     return amount;
// }

module.exports = {
    Client, client_list, getClient, getWithType
}