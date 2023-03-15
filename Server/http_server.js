const express = require("express");
const morgan = require("morgan");
const methodOverride = require("method-override");
const {getTank} = require("./tank");

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
app.use((error, req, res, next) => {
    return res.status(500).json({message: "Error Handle"});
})

app.get("/get", async(req, res) => {
    const {number} = req.query;
    // const tank = getTank(number);
    return res.status(200).json({
        angle: 10.0,
        number: number
    });
});

app.listen(process.env.HTTP_SERVER_PORT, async function() {
    console.log(`API запущена на порту ${process.env.HTTP_SERVER_PORT}`);
});