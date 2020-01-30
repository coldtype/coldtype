let karabiner = {
  "description": "coldtype-signals/f<>.txt",
  "manipulators": [
      {
          "from": {
              "key_code": "f19",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/render-all.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f18",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/render-workarea.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f17",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/render-storyboard.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f16",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/select-workarea.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f15",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/split-word-at-playhead.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f14",
              "modifiers": {
                  "mandatory": [
                      "left_command"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/capitalize.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f14",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/newline.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "f13",
              "modifiers": {
                  "optional": [
                      "any"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/coldtype-signals/newsection.txt"
              }
          ],
          "type": "basic"
      },
      {
          "from": {
              "key_code": "backslash",
              "modifiers": {
                  "mandatory": [
                      "left_command"
                  ]
              }
          },
          "to": [
              {
                  "shell_command": "echo '$RANDOM' > ~/signals/f13.txt"
              }
          ],
          "type": "basic"
      }
  ]
}

const { app, BrowserWindow, globalShortcut } = require('electron');
const WebSocket = require('ws');
const path = require("path");
const util = require("util");
const Store = require('electron-store');

const actions = [
  ["renderStoryboard", "F17"],
  ["renderWorkarea", "F18"],
  ["renderAll", "F19"],
  ["selectWorkarea", "F16"],
  ["newsection", "F13"],
  ["newline", "F14"],
  ["splitWordAtPlayhead", "F15"],
  ["capitalize", "CommandOrControl+F14"],
  ["echo", "F9"],
]

let schema = {}
actions.map(function(p) {
  schema[p[0]] = {
    type: "string",
    default: p[1]
  }
});

//const schema = schema;
//console.log(util.inspect(schema, {showHidden:false, depth:null}));

const store = new Store({schema});

const port = 8007;
const wss = new WebSocket.Server({ port: port });
let ws = null;

// https://github.com/websockets/ws#server-broadcast
wss.on("connection", function connection(_ws) {
  ws = _ws;
  ws.on("message", function incoming(data) {
      wss.clients.forEach(function each(client) {
          if (client !== ws && client.readyState === WebSocket.OPEN) {
              client.send(data);
          }
      });
  });
});

console.log(path.join(__dirname, 'appicon.icns'));

function createWindow () {
  let win = new BrowserWindow({
    width: 200,
    height: 250,
    x: 0,
    y: 0,
    icon: path.join(__dirname, 'appicon.icns'),
    webPreferences: {
      nodeIntegration: true
    }
  });
  win.loadFile('index.html');
  // https://discuss.atom.io/t/set-browserwindow-always-on-top-even-other-app-is-in-fullscreen/34215/4
  //app.dock.hide();
  //win.setAlwaysOnTop(true, "floating", 1);
  //win.setVisibleOnAllWorkspaces(true);

  //const ret = globalShortcut.register('F13', () => {
  //  console.log('F13 is pressed');
  //})

  //if (!ret) {
  //  console.log('registration failed')
  //}

  // to make sure the file exists
  store.set("echo", "F9");

  actions.map(function(action_spec) {
    let action = action_spec[0];
    let shortcut = store.get(action);
    console.log("registering", action, shortcut);
    const ret = globalShortcut.register(shortcut, () => {
      ws.send(JSON.stringify({"shortcut":action}));
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