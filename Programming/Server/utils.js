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
    },
    getAngle(from, to) {
        const a = to.x - from.x
        const b = to.y - from.y
        let phi = 0
        if (a >= 0 && b >= 0) {
            phi = 0
        } else if (a >= 0 && b < 0) {
            phi = 90
        } else if (a < 0 && b < 0) {
            phi = 180
        } else if (a < 0 && b >= 0) {
            phi = 270
        }
        return Math.abs(b) / Math.abs(a) + phi
    },
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}