from coldtype.renderer import Renderer

"""
An example of how to call the Coldtype renderer directly,
without the need to use the command line at all
(mostly useful if you’re batch-rendering fully written animations)
"""

_, parser = Renderer.Argparser()
parsed = parser.parse_args(["examples/animations/simplevarfont.py", "-a"])
Renderer(parsed).main()