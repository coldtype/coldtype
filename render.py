#!/usr/bin/env python

from coldtype.renderer import Renderer
from subprocess import call
from pathlib import Path

from coldtype.pens.svgpen import SVGPen
try:
    from coldtype.pens.drawbotpen import DrawBotPen
except:
    # Todo attempt to import CairoPen instead
    pass


class DefaultRenderer(Renderer):
    async def on_start(self):
        if self.args.icns:
            await self.render_iconset()
        elif self.args.svg_icons:
            await self.render_svg_icons()
    
    async def render_svg_icons(self):
        page = self.program["page"]
        render_data = self.program["render_data"]

        if render_data.get("output_dir"):
            icon_output = render_data["output_dir"]
        else:
            icon_output = self.filepath.parent / (self.filepath.stem + "_svg_icons")
        icon_output.mkdir(parents=True, exist_ok=True)

        for k, v in self.program.items():
            if hasattr(v, "renderable"):
                prefix = render_data.get("output_prefix", "")
                icon_path = icon_output / (prefix + v.__name__ + ".svg")
                print(icon_path)
                result = v()
                svg = SVGPen.Composite(result, page, viewBox=True)
                icon_path.write_text(svg)

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

if __name__ == "__main__":    
    pargs, parser = Renderer.Argparser()
    parser.add_argument("-i", "--icns", action="store_true", default=False)
    parser.add_argument("-si", "--svg-icons", action="store_true", default=False)

    DefaultRenderer(parser).main()