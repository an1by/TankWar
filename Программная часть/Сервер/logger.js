const colors = require('colors');

module.exports = {
    success(message) {
        console.log(`[V] ${message}`.green)
    },
    warning(message) {
        console.log(`[!] ${message}`.yellow)
    },
    error(message) {
        console.log(`[X] ${message}`.red)
    },
    info(message) {
        console.log(`[O] ${message}`.cyan)
    }
}