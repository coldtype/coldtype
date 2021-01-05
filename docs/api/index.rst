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

.. rubric:: Geometry Classes

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.geometry.Point
    coldtype.geometry.Rect

.. rubric:: Vector/Path Classes

.. autosummary::
    :toctree: reference
    :template: module.rst

    coldtype.pens.datpen.DATPen
    coldtype.pens.datpen.DATPenSet

Getting from text to vector
---------------------------

The most important thing to understand is that text can be turned into vectors via the ``.pen`` or ``.pens`` methods available on both ``StyledString`` and ``Composer`` — ``.pen`` gets you a single vector representation of a piece of text (aka a ``DATPen``), while ``.pens`` gets you a structured list of DATPen’s, aka a ``DATPenSet``.