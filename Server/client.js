const {createAddress} = require("./utils");
let client_list = []

class Client {
    constructor(socket) {
        this.socket = socket
        client_list.push(this)
    }
    address() {
        return createAddress(this.socket)
    }
    disconnect() {
        for (let i = 0; i < client_list.length; i++) {
            let client = client_list[i]
            if (client.address() === this.address()) {
                client.socket.write(JSON.stringify({"command": "disconnect"}))
                client_list.splice(i, 1);
            }
        }
    }
}

function getClient(address) {
    for (let client in client_list) {
        if (client.address() === address)
            return client;
    }
    return undefined;
}

module.exports = {
    Client, client_list, getClient
}