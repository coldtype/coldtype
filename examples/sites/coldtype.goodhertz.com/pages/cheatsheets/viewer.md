---
title: "Viewer Cheatsheet"
---

The most common viewer shortcuts:

* ``spacebar`` play the animation
* ``<left>`` go back one frame
* ``<right>`` go forward one frame
* ``shift+<left>`` go back ten frames
* ``shift+<right>`` go forward ten frames
* ``a`` render all the frames of the animation to disk
* ``cmd+a`` render just the current frame to disk
* ``,`` display the rendered version of a frame (and hit ``,`` again to display the live version) — in general this is useful if you want to play the disk-rendered version of an animation (for playing back at correct framerate/speed if animation generation is complex & consequently not realtime)
* ``.`` toggle audio support (if you have the ``[audio]`` extra successfully installed)
* ``<home>`` go to frame 0
* ``q`` quits viewer and kills running coldtype program (equivalent to ctrl-c in command-line or hitting the X in the viewer window)
* ``r`` trigger an arbitrary ``release`` function defined in your source
* ``b`` trigger an arbitrary ``build`` function defined in your source

Utilities:

* ``v`` opens the automatic timeline viewer (only applicable for animations, mostly used for MIDI and AsciiTimeline-based animations)
* ``p`` prints the current tree
* ``u`` loads the next file in the directory (sorted alphabetically)
* ``y`` loads the previous file in the directory (sorted alphabetically)
* ``s`` shows the current file output directory in the finder


## Command-line window modifications

To "pin" the window to corner of your screen, use the window-pin ``-wp`` argument and pass a compass direction (NE, SE, SW, NW), i.e. ``coldtype my-program.py -wp SE`` to have the window appear in the south-east corner of your screen

To remove the window background and chrome and make the window itself completely transparent, pass ``-wt 1`` as an argument, i.e. ``coldtype my-program.py -wt 1``

To change the initial scale of the window, pass the preview-scale argument ``-ps 2`` (for example), to get a double-sized window, i.e. ``coldtype my-program.py -ps 2``

To change the opacity of your graphics displayed in the window, pass the window-opacity argument ``-wo 0.5`` (for example), to get a half-transparent window, i.e. ``coldtype my-program.py -wo 0.5``

(All of these arguments can be combined, i.e. a window pinned to the south-west corner of your screen, with no background, 0.75 transparency, and a default size of 0.5x, would be: ``coldtype my-program.py -wt 1 -wp SW -wo 0.75 -ps 0.5``)