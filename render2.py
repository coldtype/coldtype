#!/usr/bin/env python

from coldtype.renderer import Renderer
from coldtype.pens.drawbotpen import DrawBotPen
from subprocess import call


class DefaultRenderer(Renderer):
    async def on_start(self):
        if self.args.icns:
            await self.render_iconset()

    async def render_iconset(self):
        # inspired by https://retifrav.github.io/blog/2018/10/09/macos-convert-png-to-icns/
        page = self.program["page"]
        render_fn = self.program["render_icon"]
        
        iconset_source = self.filepath.parent.joinpath(self.filepath.stem + "_source")
        iconset_source.mkdir(parents=True, exist_ok=True)
        iconset = self.filepath.parent.joinpath(self.filepath.stem + ".iconset")
        iconset.mkdir(parents=True, exist_ok=True)

        d = 1024
        while d >= 16:
            result = render_fn(d)
            path = iconset_source.joinpath(f"source_{d}.png")
            DrawBotPen.Composite(result, page, str(path), scale=1)
            for x in [1, 2]:
                if x == 2 and d == 16:
                    continue
                if x == 1:
                    fn = f"icon_{d}x{d}.png"
                elif x == 2:
                    fn = f"icon_{int(d/2)}x{int(d/2)}@2x.png"
                call(["sips", "-z", str(d), str(d), str(path), "--out", str(iconset.joinpath(fn))])
            d = int(d/2)
        
        call(["iconutil", "-c", "icns", str(iconset)])


parser = Renderer.Argparser()
parser.add_argument("-i", "--icns", action="store_true", default=False)
DefaultRenderer(parser).main()