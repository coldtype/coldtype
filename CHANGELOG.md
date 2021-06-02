# Changelog

Starting at 0.5.0, all notable changes to Coldtype will be described here (briefly).

## [0.5.0] - 2021-06-02
### Added
- `coldtype.fx.skia`
- `SkiaImage` (subclass of `DATImage`, which has been moved to `coldtype.img` module)
### Removed
- `.phototype`/`.color_phototype` methods on `DATPen` — these are now "chainable" methods in the _coldtype.fx.skia_ module, and can be applied by importing ala `from coldtype.fx.skia import phototype` and then chaining to a pen, `.ch(phototype(...))`