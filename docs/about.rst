About
=====

What is Coldtype?
-----------------

**A cross-platform library to help you precisely & programmatically do high-quality display typography with Python.**

`Problem`: you want to create images and animations with code, but you don’t want to sacrifice high-quality display typography.

`Solution`: Coldtype (or DrawBot!)

Yes, there are lots of ways to set type with code. Most ways — HTML/CSS/JS, Processing, etc. — are great for 90% of what most people want to do with Latin-based writing systems. Then the road runs out and you can’t do anything else.

Coldtype is an offroad vehicle that lets you keep driving where there are no roads. Like many vehicles built for specialized use, it is not user-friendly. It has no doors (please climb in through the window), and the steering wheel is not very intuitive, also it’s a stick-shift, and you should probably know how to code (or be willing to learn) if you’re going to drive it alone out into the desert. (I apologize for how automotive this metaphor is getting. Probably should’ve gone with some metaphor about people making custom synthesizers in the 70s.)

What about DrawBot?
-------------------

If you’ve heard of `DrawBot <http://www.drawbot.com/>`_ — another offroad vehicle that lets you drive where you want — you may be wondering how Coldtype is different. The answer is that Coldtype provides a very different programming idiom, one based around creating and modifying structured data, rather than — as is common in most “creative coding” platforms (including DrawBot and Processing) — providing a metaphorical canvas that you render to directly.

(I should point out that DrawBot is fantastic and that Coldtype would not exist without DrawBot, mostly because using DrawBot was my first time driving in the typographical offroad. That said, Coldtype mostly exists as a response to things I found awkward when programming animations with DrawBot.)

What about Adobe products?
--------------------------

I’ve learned over the last few years to distrust any `Type Tool` in an Adobe product (or anywhere else). Yes, those can be very good — like HTML+CSS — for doing simple Latin-based typography for static designs. But then, all of a sudden, they are very bad. You can think of Adobe products as a train that you get on and you can fall asleep in a nice seat and the train will get you where you want to go, except when you wake up and realize you wanted to go somewhere the train doesn't go and then you’re like... `dang, do I have to walk?` (Walking in this metaphor is when you right click and hit `Convert to Outlines`.)

Walking can be a lot of fun, and you get to see a lot. Drawing is a lot like walking. Fabulous exercise; you learn a lot. But sometimes you want to get there faster or you want to go farther.

Why “coldtype”?
---------------

Coldtype refers to the short-lived era of early semi-digital typesetting (extending roughly from the late 1940s to the widespread adoption of personal computing in the early 1990s), during which time computers were used to control various analog photographic processes for setting type, technologies now known, usually, as “phototype,” but sometimes also known as “coldtype,” to distinguish it from hot-metal type, which was the previous standard. (And it was hot — Linotype machines were known to squirt molten lead out at the operator.)

Phototype/coldtype was a hybrid moment in typographic history, and a fascinating one — 500 years of metal-type-based assumptions were upended all at once, as letters now did not need to live on a rectangular metal body, meaning they could get really close together. (Which, for me, really helps explain, like, all of graphic design between 1960 and 1980.)

Also originally I thought it was a funny name because I wanted to make a very fast typesetting library using Harfbuzz, and when computers run quickly and efficiently, they remain cold. Of course, I now regularly use all 8 cores of my computer when I use render 1000s of frames at once using coldtype, which gets the fans going. But the name still sounds good.

Is Coldtype capitalized?
------------------------

I can’t decide, as you may be able to tell from this documentation’s inconsistent capitalization scheme.

Who works on this?
------------------

This library is mostly the work of me, Rob Stenson, but I want to acknowledge the work of some people who’s open-source code helped bring this project to life:

* ``coldtype.pens.outlinepen`` contains code written by Frederik Berlaen, Copyright (c) 2016
* ``coldtype.pens.translationpen`` contains code written by Loïc Sander, Copyright (c) 2014
* ``coldtype.fontgoggles`` contains parts of the `FontGoggles <https://github.com/justvanrossum/fontgoggles>`_ codebase, written by Just van Rossum, Copyright (c) 2019 Google, LLC. Just is also responsible for DrawBot which the main inspiration behind this project.
* Mutator Sans included for testing was written by Erik van Blokland, Copyright (c) 2017
- Recursive Mono Casual Italic is an `open-source typeface <https://github.com/arrowtype/recursive>`_ by @arrowtype
- Coldtype Obviously is a open-source subset of the commercially-available font `Obviously <https://ohnotype.co/fonts/obviously>`_ by OHno Type Co; s/o to James Edmondson for donating those 8 characters to this project.
- Coldtype relies heavily (via FontGoggles) on the incredible `HarfBuzz <https://github.com/harfbuzz/harfbuzz>` text shaping library.
