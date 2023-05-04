const express = require("express");
const morgan = require("morgan");
const methodOverride = require("method-override");

const app = express();

app.use(morgan("combined"));
app.use(express.json());
app.use(methodOverride());
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Content-Type, Content-Length");
    res.header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, PATCH, DELETE");
    next();
});

app.use(express.static('public'))

let url = ''

app.get('/', (req, res) => {
    return res.render("index",
        {
            srcAttr: url
        }
    );
})

app.use((error, req, res, next) => {
    return res.status(500).json({message: "Error Handle"});
})

app.listen(process.env.HTTP_SERVER_PORT, async function() {
    console.log(`API запущена на порту ${process.env.HTTP_SERVER_PORT}`);
});

module.exports = {
    setUrl(uri) {
        url = uri
    }
}