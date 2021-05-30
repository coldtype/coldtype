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

### GCP

PyTorch images seem to work nicely (`c2-deeplearning-pytorch-1-8-cu110-v20210512-debian-10`), not sure this is a real link: https://console.cloud.google.com/compute/imagesDetail/projects/ml-images/global/images/c2-deeplearning-pytorch-1-8-cu110-v20210512-debian-10?folder=&organizationId=&project=uplifted-sol-90414
https://console.cloud.google.com/compute/imagesDetail/projects/ml-images/global/images/c2-deeplearning-pytorch-1-8-cu110-v20210512-debian-10

SSH w/ cloud console, then:

- `sudo apt install libgl1-mesa-glx` # https://github.com/conda-forge/pygridgen-feedstock/issues/10
- `git clone https://github.com/goodhertz/coldtype`
- `cd coldtype`
- `pip install -e .`
- `coldtype examples/animations/house.py -a -mp -cpu -ns` # -tc 32 (if it’s a big 32-instance)

### Second Monitor

`coldtype examples/simplest.py -mn list`
should print out names of monitors, then you match then (can be a substring) like this:
`coldtype examples/simplest.py -mn SAM -wcs 1.0 -wp C`

### Installing with extras directly from git

`pip install git+https://github.com/goodhertz/coldtype#egg=coldtype[viewer,experimental]`