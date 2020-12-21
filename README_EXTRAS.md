### MIDI

Todo

### Global hotkeys

Uses pynput, but on Mac permissions are a pain now: [helpful instructions](https://textexpander.com/kb/mac/textexpander-is-forcing-me-to-enable-access-for-assistive-devices-how-and-what-is-that/#:~:text=Go%20to%20the%20System%20Preferences,%E2%80%9CEnable%20for%20assistive%20devices.%E2%80%9D)

### Mouse-passthrough on glfw

Actually specifying it might not be necessary? Seems to work on my machine
```
brew install glfw --HEAD
PYGLFW_LIBRARY=/usr/local/Cellar/glfw/HEAD-0b9e48f/lib/libglfw.3.4.dylib
```