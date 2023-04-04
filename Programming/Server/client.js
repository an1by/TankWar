const {createAddress} = require("./utils");
let client_list = []

class Client {
    constructor(socket, type) {
        this.socket = socket
        this.type = type
        this.address = createAddress(this.socket)
        this.step = true // true / false
        client_list.push(this)
    }
    disconnect() {
        for (let i = 0; i < client_list.length; i++) {
            let client = client_list[i]
            if (client.address === this.address) {
                if (client.socket)
                    client.socket.write(JSON.stringify({"command": "disconnect"}))
                client_list.splice(i, 1);
            }
        }
    }
    send_data(data) {
        this.socket.write(JSON.stringify(data), 'utf-8')
    }
}

function getWithType(type) {
    let array = []
    for (let client in client_list) {
        if (client.type === type)
            array.push(client)
    }
    return array;
}

function getClient(address) {
    for (let client in client_list) {
        if (client.address === address)
            return client;
    }
    return undefined;
}

function countClientType(type) {
    return getWithType(type).length
}

module.exports = {
    Client, client_list, getClient, getWithType, countClientType
}