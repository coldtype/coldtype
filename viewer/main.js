const { app, BrowserWindow, globalShortcut } = require('electron');
const WebSocket = require('ws');
const path = require("path");
const util = require("util");
const Store = require('electron-store');

let schema = {
  always_on_top: {
    type: "boolean",
    default: false,
  },
  keyboard_shortcuts: {
    type: "array"
  }
}

//console.log(util.inspect(schema, {showHidden:false, depth:null}));

const store = new Store({schema});

const port = 8007;
const wss = new WebSocket.Server({ port: port });
let ws = null;

// https://github.com/websockets/ws#server-broadcast

function broadcast(data) {
  wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN) {
        client.send(data);
    }
  });
}

wss.on("connection", function connection(_ws) {
  ws = _ws;
  ws.on("message", function incoming(data) {
    broadcast(data);
  });
});

console.log(path.join(__dirname, 'appicon.icns'));

function createWindow () {
  let win = new BrowserWindow({
    width: 200,
    height: 550,
    x: 0,
    y: 0,
    icon: path.join(__dirname, 'appicon.icns'),
    webPreferences: {
      nodeIntegration: true
    }
  });

  win.loadFile('index.html');

  // https://discuss.atom.io/t/set-browserwindow-always-on-top-even-other-app-is-in-fullscreen/34215/4

  if (store.get("always_on_top")) {
    app.dock.hide();
    win.setAlwaysOnTop(true, "floating", 1);
    win.setVisibleOnAllWorkspaces(true);
  }

  // to make sure the file exists
  store.set("config", "test");

  let shortcuts = store.get("keyboard_shortcuts", []);

  shortcuts.map(function(shortcut_spec) {
    let action = shortcut_spec[0];
    let shortcut = shortcut_spec[1];
    console.log("registering", action, shortcut);
    const ret = globalShortcut.register(shortcut, () => {
      broadcast(JSON.stringify({"trigger_from_app": true, "action": action}));
    })
    if (!ret) {
      console.log("failed to register", action, shortcut);
    }
  });
}

app.on('ready', createWindow);

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})