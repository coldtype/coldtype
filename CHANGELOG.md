# Changelog

Starting at 0.5.0, all notable changes to Coldtype will be described here (briefly). Edit: looks like I forgot this existed, so we're starting again at 0.5.16

## [0.5.0] - 2021-06-02
### Added
- `coldtype.fx.skia`
- `SkiaImage` (subclass of `DATImage`, which has been moved to `coldtype.img` module)
### Removed
- `.phototype`/`.color_phototype` methods on `DATPen` — these are now "chainable" methods in the _coldtype.fx.skia_ module, and can be applied by importing ala `from coldtype.fx.skia import phototype` and then chaining to a pen, `.ch(phototype(...))`

## [0.5.16] - 2021-08-03
### Added
- Minor improvements to the self-rasterizing/drawbot-renderer, to support transparent backgrounds
### Removed
- `@drawbot_script` and `@drawbot_animation` from the global import; now reside and can be imported from `coldtype.drawbot` module

## [0.5.17] - 2021-08-06
### Fixed
- Quoting paths in `blend_frame`
### Removed
- `unicodedata2` from primary installation requirements, in order to make blender installation smoother (i.e. not require Include header-copying from python source tarball) — thanks @colinmford!

## [0.6.0] - 2021-08-30
### Added
- New features for managing meshes in BlenderPen
- embedded profiles, so `-p b3d` should now work globally
### Removed
- `duration` keyword for `@animation`, since it’s redundant to `timeline=<int>` shortcut

## [0.6.1] - 2021-08-31
### Added
- Support for `kp` and `tu` in `Glyphwise`

## [0.6.2] - 2021-09-01
### Added
- Support for single-char `Glyphwise`
- `Glyphwise` now returns `DATPens`, not `DraftingPens`

## [0.6.3] - 2021-09-07
### Added
- Support for multi-return styler fn for `Glyphwise`
- Coldtype panel for `@b3d_sequencer`

## [0.6.6] - 2021-09-10
### Added
- Better MIDI primitives
- `coldtype midi` midi viewer

## [0.6.8] - 2021-09-16
### Added
- Better axidraw primitives in new `coldtype.axidraw` namespace, demonstrated in `test/visuals/test_axidraw.png`
- New `numpad` special variable that can handle up to 9 special actions, triggerable from the numpad with the viewer enabled
### Removed
- Dependency on `PyOpenGL-accelerate` in the `[viewer]` extra — not really sure why that was there to begin with.

## [0.6.9] - 2021-09-20
### Added
- Restored some audio capabilities, via `audio=` keywords and the new `ConfigOption.EnableAudio`/`KeyboardShortcut.EnableAudio`

## [0.7.0] - 2021-09-26
### Fixed
- General tidying, particularly for use in `[notebook]`
### Removed
- Dependency on `noise` in `[viewer]`

## [0.7.1] - 2021-09-28
### Added
- Support for configurable `BLENDER_APP_PATH`
- Better support for Windows-Blender workflow

## [0.7.2] - 2021-09-29
### Added
- Support for gif export in `@notebook_animation.show`

## [0.7.3] - 2021-10-07
### Added
- `strip=` kwarg on StSt (defaulting to `True`) so incoming text is automatically stripped (but can be overriden as in the `Glyphwise` use of `StSt`)
- `coldtype.blender.fluent` experimental chainable interface for direct manipulation of blender objects

## [0.7.4] - 2021-10-21
### Added
- Support for lineTo's in `distribute_on_path`
- More `coldtype.blender.fluent` interface
- Ability to exit from renderer with -1 in `prenormalize_filepath`

## [0.7.5] - 2021-10-25
### Added
- `@ui` decorator idea, to be used/tested in Goodhertz plugin-builder

## [0.7.6] - 2021-11-02
### Added
- `.depth`, `.split`, `.wordPens`, `.walkp`
- `î` and `ï` for `index` and `indices`, also both of those on `DraftingPen` now, since they shadow functionality of `mod_contour` and `map_points`
- `utag` in walk.data
- camelCase throughout examples, headed towards standardizing on that
- `.geti` for time-based fetch in `AsciiTimeline`
### Fixed
- `style=` on precomposed/@renderable-cached

## [0.8.0] - 2021-12-13
### Added
- `MidiTimeline` to replace `MidiReader` (`MidiTimeline` uses standard `Timeline` capabilities rather than Midi-specifi classes)
- `AsciiTimeline` improvements and changed api, old `[]`-style access replaced by `.ki`; keyframe support also added, via `.kf`; many new examples in `examples/animations/ascii_*`
- `Easeable` class to encapsulate all easing functionality, i.e. a `Timeable` bound to a frame value, meaning frame values can now be implied on all `@animation`-bound timelines (via `Timeline.hold`)
- Generic lyric-video sentence building on timelines, available contextually as `.words` on a timeline (example in `examples/animations/ascii_words.py`) (adapted from older `Sequence` class (not recommended for use), originally developed for lyric video animation in Premiere, though works better now with Blender)
- Automatic timeline viewer, available with `-tv 1` command-line arg or toggleable with `V` key in viewer app
- A lot more examples
- Normalized behavior of `point=` handling in `.scale`/`.rotate`/`.skew`
- Manual-drive `BlenderTimeline`
### Removed
- Implicit `BlenderTimeline` on `@b3d_animation` and `@b3d_sequencer`
- `.progress` method (in favor of new `Easeable` apis)
### Changed
- `.e` now defaults to `loops=1`, rather than `loops=0`

## [0.8.1] - 2021-12-28
### Fixed
- Audio support via `pyaudio`

## [0.8.2] - 2022-01-10
### Fixed
- Error where windows can't watch non-existent file
- Error where windows barfs on os.uname

## [0.9.0] - 2022-01-18
### Added
- `coldtype.runon.runon` abstraction for chained/fluent method calling on nested lists
- `coldtype.runon.path` i.e. `P` as a drop-in replacement for `DATPen/DATPens` (should be fully backwards compatible), which extends `coldtype.runon.runon`
### Fixed (maybe)
- File watching on windows
### Removed
- `watchdog` dependency (using `stat().st_mtime` polling instead now since we’re already running an event loop out of necessity for the viewer)

## [0.9.1] - 2022-01-31
### Added
- `memory=` keyword for renderables (attempting some kind of support for processing-style live-coded animations)
- `fvar_<x>` generic style for addressing sorted variable font axes
- `x` key for xray mode
- `g` key for grid mode
- `p` key to print renderable content

## [0.9.2] - 2022-02-21
### Added
- support for platform-specific config files, `.coldtype.mac.py`, `.coldtype.win.py`, `.coldtype.lin.py`
- minor Blender improvements for 3D workflow

## [0.9.3] - 2022-03-08
### Added
- `C` as valid alias for `CX` on xalign
### Fixed
- `filterContours` copy before modify
- Orphan-deletion in Blender

## [0.9.5] - 2022-03-24
### Fixed
- `bake=True` for a `@b3d_animation`

## [0.9.6] - 2022-07-13
### Fixed
- Spelling mistakes [h/t @HaydenBL]
### Added
- Tons of experimental additional functionality for more direct-style scripting of blender and forthcoming coldtype-based blender typography addon (all in fluent.py, with some supporting tweaks in other coldtyper.blender infrastructure)

## [0.9.7] - 2022-08-06
### Added
- New transparency background when `bg` not specified
- `render_bg` now defaults to `True`, since that seems to be the most common use-case
- `ufo2ft` in `[blender]` optional requirements
- simple `gifski` wrapper importable from `coldtyper.renderable.animation`
### Fixed
- Better error message when trying to "release" via ffmpeg but no files have been rendered

## [0.9.8] - 2022-08-25
### Added
- New arg `round_result` on `SkiaImage.align`, to fix jaggy image aligning; defaults to True but is disableable

## [0.9.10] - 2022-09-25
### Fixed
- `glyph_to_uni` in packaged mode

## [0.9.11] - 2022-10-27
### Added
- `Runon.attach`
### Fixed
- Explicit include of ufoLib2 for blender

## [0.9.12] - 2022-11-02
### Added
- `P.spread` as horizontal-only counterpart to `P.stack` (paired with `P.track` and `P.lead` respectively, funny that they rhyme oppositely whoops)
### Fixed
- Default `"."` in ALL_FONT_DIRS for linux (so colab notebooks search in their uploaded files by default)

## [0.9.13] - 2022-11-08
### Added
- `Easeable.ec` as easing-cumulative (to help with partial rotations,
as in the new truchet animation examples, and examples/animations/ec.py)

## [0.9.14] - 2022-11-16
### Added
- `P.gridlayer`, `Runon.mapvch`, `Runon.mapvrc`

## [0.10.0] - 2023-01-15
### Added
- `.up` as canonical form of `.ups`
- Argument-less boolean operation methods for plural `P`
- Automatic _-prefixed versions of all P methods, to get clojure-style "phrase"-commenting
- `VERSIONS=` support for macro-like reversioning of a single animation
- `Font.LibraryFind` and `Font.LibraryList` to search font registry (mac-only, windows is excruciatingly difficult)
- `Font.names` to get style and family name of font via fontTools
### Changed
- `Mondrian` -> `Scaffold`
- `th` & `tv` (true-horizontal & true-vertical) have been renamed to potential confusion (since `th` could be taken to mean `true-height`) — these are now `tx` and `ty` respectively

## [0.10.2] - 2023-01-17
### Changed
- The Blender integration now inlines your local venv into Blender, meaning you no longer need to install any python packages into Blender's embedded python.

## [0.10.4] - 2023-01-20
### Added
- `-rar` (`--render-and-release`) command-line option to render-and-release(-and-then-quit)

## [0.10.5] - 2023-03-22
### Improved
- `Scaffold.cssgrid` now supports arbitrary regex keys in a dictionary arg for targeting multiple children at once (shown in test_scaffold.py)

## [0.10.6] - 2023-03-23
### Added
- `Runon.path` and `Runon.match` (taken from `Scaffold`) as new generic features, to regex-match on nested/slashed tags (i.e. paths)

## [0.10.7] - 2023-04-18
### Fixed
- `.ufo` font-reading on Windows

## [0.10.8] - 2023-06-11
### Fixed
- Font issue with `coldtype demo`

## [0.10.9] - 2023-06-23
### Added
- `b3denv` requirement, to help get default blender app path

## [0.10.10] - 2023-06-30
### Fixed
- `b3denv` assumes Blender exists, which is wrong

## [0.10.11] - 2023-07-31
### Added
- `P.to_code` (for a Goodhertz project that used the legacy `DATPen(s).to_code`)

## [0.10.12] - 2023-07-31
### Added
- Experimental support for reading control changes (cc messages) from midi files, via `MidiTimeline.ci` method

## [0.10.13] - 2023-08-04
### Added
- CycleVersionForward/CycleVersionBackward
- Support for _version.py-style sidecar versioning
- Support for special `__initials__` function to allow setting state from source file

## [0.10.14] - 2023-09-21
### Added
- `Rect.contains`/`Rect.__contains__`/`in` operator for Rect
- `E` and `W` supported on `pair_to_edges`
- `<` as parent ref in `Scaffold.find`
- Support `vert` as feature (without needing to specify `features=`)
- `RestartCount` concept in renderer
- `Font.Fontmake` for full font compilation to a tmp file

## [0.10.15] - 2024-03-27
### Added
- `coldtype.fx.skia.freeze` for in-memory "freezing" of vectors (to avoid recalculation)
- `Runon.collapseonce` for shallow collapsing

## [0.10.16] - 2024-05-16
### Added
- Support for skia-python 87.6 on python3.12

## [0.10.17]
### Added
- Fix for >= m87 skia-python with glfw gl-version setting (https://www.glfw.org/faq#macos / https://github.com/kyamagu/skia-python/issues/214)

## [0.10.18]
### Added
- Support for custom global hotkeys via `custom_hotkey` function in source files

## [0.10.19] - 2024-06-20
### Fixed
- High quality filter support for skia > m87

## [0.10.20] - 2024-07-23
### Fixed
- Spec <=0.4.2 for python-bidi since 0.5.0 is beefed

## [0.10.21] - 2024-09-30
### Added
- `use_skia_pathops_draw=False` kwarg override for `P.removeOverlap` to make sure we don't get all-off-curve+None quadratics in situations where we don't know how to convert that to cubics (i.e. in Blender)

## [0.10.22] - 2024-10-07
### Added
- `Rect.fit_aspect` for easily getting an aspect inscribed by a rect
- version lock on python-bidi

## [0.11.0] - 2024-12-12
Huge update, attempting to future proof things
### Added
- External dependency on coldtype/fontgoggles fork (instead of out-of-date inlined fontgoggles fork)
### Fixed
- Gonna be honest — fixed lots of stuff, should’ve been writing down what I was fixing!

## [0.11.1] - 2024-12-15
### Fixed
- Make sure coldtype.drawbot does not require skia-python (via incorrect import)
- try/except for filmjitter in coldtype.raster
- Don’t enable audio if audio can’t be enabled (print instructions on enabling audio instead)

## [0.11.2] - 2025-01-26
### Added
- `Font.instances` to get variable font instance information
- `coldtype instances font=<font-search>` tool
- `ººBLENDERINGºº` variable to quickly know if your code is running in blender or as a blender-renderer
- `P.trim_start` and `P.trim_end` to quickly drop points from either end of a curve
### Changed
- `P.boxCurveTo` `factor=` keyword now expects float, not int
### Fixed
- Updated coldtype-fontgoggles to latest to avoid Windows thinking it could do objc

## [0.11.3] - 2025-01-28
### Added
- Experimental support for limited keyboard layout remapping via command line -kl argument

## [0.11.4] - 2025-02-20
### Added
- `ViewerSoloFirst` and `ViewerSoloLast` shortcuts
### Changed
- `VIEWER_SOLO` is now a config option, not a one-off cli arg in renderer

## [0.11.5] - 2025-03-04
### Added
- `set_709` on `animation.export`/`FFMPEGExport` (so you can use older `ffmpeg` releases to export animations)

## [0.11.6] - 2025-03-11
### Added
- better support for custom output with ct viewseq
- experimental support for `Theme` class to set multiple color styles from a single object
### Fixed
- blender venv-inlining now look for a "src" directory if it exists (to match new pyproject.toml-enforced directory structure)