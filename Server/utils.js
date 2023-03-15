module.exports = {
    createAddress(client) {
        return client && client.remoteAddress && client.remotePort ? (client.remoteAddress + ':' + client.remotePort).slice(7) : undefined
    },
    createPosition(position) {
        const data = position.split(';');
        switch (data.length) {
            case 2:
                return {
                    x: parseInt(data[0]),
                    y: parseInt(data[1])
                }
            case 3:
                return {
                    x: parseInt(data[0]),
                    y: parseInt(data[1]),
                    angle: parseFloat(data[2])
                }
            default:
                return undefined
        }
    }
}