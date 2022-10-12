#!/usr/bin/env python

from coldtype import *
from coldtype.renderer import Renderer
import subprocess

all_docs = []

sources = list(Path("docs").glob("**/*.rst"))

for p in sources:
    print(">", p)
    if not p.name.startswith("_"):
        all_docs.append(p)
    all_docs = sorted(all_docs)


class DocsWriter(Renderer):
    def on_stdin(self, stdin):
        stdin = stdin.strip()
        if stdin == "upload":
            self.upload()
        else:
            super().on_stdin(stdin)
    
    # def initialize_gui_and_server(self):
    #     self.webserver = subprocess.Popen(["python", "-m", "http.server", "8003", "-d", "docs/_build/html"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #     super().initialize_gui_and_server()
    
    # def on_exit(self, restart=False):
    #     self.webserver.terminate()
    #     super().on_exit(restart=restart)
    
    def buildrelease_fn(self, fnname="release"):
        if fnname != "build":
            return super().buildrelease_fn(fnname=fnname)

        def build_docs(passes):
            from shutil import copy2
            imgs = {}
            for pss in passes:
                img = None
                if isinstance(pss.render, animation):
                    gif = Path(str(pss.render.output_folder) + ".gif")
                    if gif.exists() and gif not in imgs:
                        img = gif
                        imgs[gif] = 1
                else:
                    img = pss.output_path
                
                if not img:
                    continue
                try:
                    dst = Path("docs/_static/renders")
                    dst.mkdir(parents=True, exist_ok=True)
                    print(img)
                    copy2(img, dst / img.name)
                    print("COPYING", img.name)
                except FileNotFoundError:
                    print("FileNotFound", img)

            if True:
                owd = os.getcwd()
                try:
                    os.chdir("docs")
                    os.system("make clean")
                    os.system("make html")
                finally:
                    os.chdir(owd)
        
        return build_docs
    
    def upload(self):
        os.system("./upload_docs.sh")


def main():
    pargs, parser = Renderer.Argparser(name="docs-writer", file=True)
    DocsWriter(parser).main()

if __name__ == "__main__":
    main()