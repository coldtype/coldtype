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