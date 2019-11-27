const { app, BrowserWindow } = require('electron');
const WebSocket = require('ws');

const port = 8007;
const wss = new WebSocket.Server({ port: port });

// https://github.com/websockets/ws#server-broadcast
wss.on("connection", function connection(ws) {
    ws.on("message", function incoming(data) {
        wss.clients.forEach(function each(client) {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(data);
            }
        });
    });
});

function createWindow () {
  let win = new BrowserWindow({
    width: 200,
    height: 250,
    x: 0,
    y: 0,
    icon: __dirname + 'appicon.icns',
    webPreferences: {
      nodeIntegration: true
    }
  });
  win.loadFile('index.html');
  // https://discuss.atom.io/t/set-browserwindow-always-on-top-even-other-app-is-in-fullscreen/34215/4
  app.dock.hide();
  win.setAlwaysOnTop(true, "floating", 1);
  win.setVisibleOnAllWorkspaces(true);
}

app.on('ready', createWindow);