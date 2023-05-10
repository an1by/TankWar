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
        const b = to.x - from.x
        const a = to.y - from.y
        
        let alpha = 0
        if (b !== 0 && a !== 0) {
            const c = Math.sqrt(Math.pow(a, 2) + Math.pow(b, 2))
            let w = Math.pow(a, 2) - Math.pow(b, 2) - Math.pow(c, 2)
            let z = -2 * Math.abs(b) * Math.abs(c)
            alpha = Math.acos(w/z) * 180 / Math.PI
            alpha = Math.round(alpha)
        } else {
            alpha = b >= 0 ? 0 : 180
        }
        return a >= 0 ? alpha : -alpha
    },
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}