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