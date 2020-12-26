#!/usr/bin/env python

from coldtype import *
from coldtype.renderer import Renderer
import subprocess

all_docs = []

sources = list(Path("docs").glob("**/*.rst"))
#sources.extend(list(Path("docs").glob("test_*.md")))

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
    
    def on_message(self, message, action):
        if action == "next_test":
            self.load_doc(+1)
        elif action == "prev_test":
            self.load_doc(-1)
        else:
            super().on_message(message, action)
        
    def load_doc(self, inc):
        if hasattr(self, "doc_index"):
            self.doc_index += inc
        else:
            self.doc_index = 0
        if self.doc_index == -1:
            self.doc_index = len(all_docs) - 1
        elif self.doc_index == len(all_docs):
            self.doc_index = 0
        
        doc_path = all_docs[self.doc_index]
        print("---" * 20)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>", doc_path)
        self.reset_filepath(str(doc_path))
        self.reload_and_render(Action.PreviewStoryboard)
    
    def initialize_gui_and_server(self):
        self.webserver = subprocess.Popen(["python", "-m", "http.server", "-d", "docs/_build/html"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        super().initialize_gui_and_server()
    
    def on_exit(self, restart=False):
        self.webserver.terminate()
        super().on_exit(restart=restart)
    
    def release_fn(self):
        candidate = super().release_fn()

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
                    copy2(img, dst / img.name)
                    print("COPYING", img.name)
                except FileNotFoundError:
                    print("FileNotFound", img)
            owd = os.getcwd()
            try:
                os.chdir("docs")
                os.system("make clean")
                os.system("make html")
            finally:
                os.chdir(owd)
        
        if candidate:
            def wrapped(passes):
                candidate(passes)
                build_docs(passes)
            return wrapped
        else:
            return build_docs
    
    def upload(self):
        os.system("./upload_docs.sh")


def main():
    pargs, parser = Renderer.Argparser(name="docs-writer", file=True)
    DocsWriter(parser).main()

if __name__ == "__main__":
    main()