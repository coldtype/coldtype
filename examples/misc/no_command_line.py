from coldtype.renderer import Renderer

"""
`python examples/misc/no_command_line.py`

An example of how to call the Coldtype renderer directly,
without the need to use the command line at all
(mostly useful if you’re batch-rendering fully written animations)

That said, if you take out the "-a" arg, this should run exactly
like the normal coldtype viewer — potentially useful for a situation
in which it’s difficult to access the `coldtype` bin command, since
you could run this with just the standard `python` bin command
"""

_, parser = Renderer.Argparser()
parsed = parser.parse_args(["examples/animations/simplevarfont.py", "-a"])
Renderer(parsed).main()