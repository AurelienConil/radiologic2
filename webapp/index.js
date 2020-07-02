
//--------------------------------------------------
//  Basic Express serveur
//--------------------------------------------------

const express = require('express');
const app = express();
const cors = require("cors")
const serveIndex = require('serve-index');
const expressUpload = require('express-fileupload');

//location to /dist with final deployment
app.use(cors())
app.use(expressUpload({
    createParentPath:true
}))
app.use('/json',
function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write('<form action="fileupload" method="post" enctype="multipart/form-data">');
    res.write('<input type="file" name="settingsFile"><br>');
    res.write('<input type="submit">');
    res.write('</form>');
    return res.end();
})
app.post('/fileupload', async (req, res) => {

    try {
        if(!req.files) {
            res.send({
                status: false,
                message: 'No file uploaded'
            });
        } else {
           
            let jsonFile = req.files.settingsFile;
            
            // jsonFile.mv('public/dist/datajson.json');
jsonFile.mv('../datajson.json')
            //send response
            res.send({
                status: true,
                message: 'File is uploaded',
                data: {
                    name: jsonFile.name,
                    mimetype: jsonFile.mimetype,
                    size: jsonFile.size
                }
            });
        }
    } catch (err) {
        res.status(500).send(err);
    }
});
app.use('/datajson.json',express.static('../datajson.json'))
app.use('/UserSettings.json',express.static('../UserSettings.json'))
app.use('/', express.static('public/dist'))
app.use('/', serveIndex('public/dist'))

app.listen(3000, () => console.log('Server OPEN on port 3000!'));




//--------------------------------------------------
//  Bi-Directional OSC messaging Websocket <-> UDP
//--------------------------------------------------
var osc = require("osc"),
    WebSocket = require("ws");
const { fstat } = require('fs');

var getIPAddresses = function () {
    var os = require("os"),
        interfaces = os.networkInterfaces(),
        ipAddresses = [];

    for (var deviceName in interfaces) {
        var addresses = interfaces[deviceName];

        for (var i = 0; i < addresses.length; i++) {
            var addressInfo = addresses[i];

            if (addressInfo.family === "IPv4" && !addressInfo.internal) {
                ipAddresses.push(addressInfo.address);
            }
        }
    }

    return ipAddresses;
};

var udp = new osc.UDPPort({
    localAddress: "0.0.0.0",
    localPort: 12345,
    remoteAddress: "127.0.0.1",
    remotePort: 12344
});

udp.on("ready", function () {
    var ipAddresses = getIPAddresses();
    console.log("Listening for OSC over UDP.");
    ipAddresses.forEach(function (address) {
        console.log(" Host:", address + ", Port:", udp.options.localPort);
    });
    console.log("Broadcasting OSC over UDP to", udp.options.remoteAddress + ", Port:", udp.options.remotePort);
});

udp.open();

var wss = new WebSocket.Server({
    port: 8081
});

wss.on("connection", function (socket) {
    console.log("A Web Socket connection has been established!");
    var socketPort = new osc.WebSocketPort({
        socket: socket
    });

    var relay = new osc.Relay(udp, socketPort, {
        raw: true
    });
});


