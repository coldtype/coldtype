API
===

**Work in progress**

N.B. All of the following are available unprefixed after a ``from coldtype import *``, or are available at the specified prefix locations after an ``import coldtype``.

.. rubric:: Textsetting Classes

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.text.reader.Style
    coldtype.text.reader.StyledString
    coldtype.text.composer.Composer

The most important thing to understand is that textsetting classes can be turned into vector classes via the ``.pen`` or ``.pens`` methods available on both ``StyledString`` and ``Composer`` — ``.pen`` gets you a single vector representation of a piece of text (aka a ``DATPen``), while ``.pens`` gets you a structured list of DATPen’s, aka a ``DATPens``.

.. rubric:: Vector/Path Classes

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.pens.datpen.DATPen
    coldtype.pens.datpen.DATPens

.. rubric:: Rendering Decorators

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.renderable.renderable
    coldtype.renderable.animation.animation

.. rubric:: Time/Timing Classes

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.time.Frame
    coldtype.time.Timeable
    coldtype.time.Timeline
    coldtype.time.Timing
    coldtype.time.loop.Loop
    coldtype.time.easing.ease