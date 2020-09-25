# Notes towards a better README

### Programming philosophy

Here is a free-associated list of things that I think define the general vibe of programming in Coldtype (a work-in-progress)

- Chained mutation/transformation
    - "Chaining" in this context refers to the programming style favored by libraries like jQuery, which allows you to call multiple methods on a single line, all of which mutate the state of an object and return the object itself in each mutating call. For example:
        - `DATPen().rect(Rect(500, 500)).translate(100, 100).rotate(45)` creates a `DATPen` object, then adds a rectangle bezier to it, then translates it, then rotates it, all in a single line. In normal circumstances, programming like this is called "spaghetti" code because it's long and hard to follow, or something like that. In this case, its brevity is its benefit
        - Yes I know mutation is theoretically “bad” or whatever, yeesh, I just really love how it works in real life.
- Coldtype does not use classic "drawing"-style APIs/graphic state, though the data model of Coldtype can be (and is meant to be) serialized to any number of canvas/drawing APIs, and can be extended to any API that implements `fill`/`stroke` and `moveTo`/`lineTo`/`curveTo`

## Caveats

### What is Coldtype _not_?

- Coldtype is not good for setting large amounts of text in a single frame, because Coldtype has no line-breaking algorithms.
- This means Coldtype is probably bad for most print applications (you should use DrawBot for that, because DrawBot has line-breaking algorithms).
- In fact, Coldtype is not good at most things that normal type-setting software is good at. Generally-speaking, the goal of this library is to give you exactly what you want, rather than a “best guess.” For example:
    - Coldtype does not implement fallback support (expect to see some `.notdef`s)

### How is this different from DrawBot?

- Use whatever text editor you want
- Cross-platform
- Does not rely on Apple’s CoreText engine or the mostly deprecated APIs that DrawBot uses to interact with it
- Really only a small subset of what DrawBot, by leveraging CoreText and CoreImage, can do (which is a good thing to me, because I only ever used DrawBot for typography anyway)
- Little-to-no image support (some, but it is vvv primitive)