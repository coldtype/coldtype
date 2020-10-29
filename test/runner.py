#!/usr/bin/env python

from coldtype import *
from coldtype.renderer import Renderer

all_tests = []

sources = list(Path("test").glob("test_*.py"))
sources.extend(list(Path("test").glob("test_*.md")))

for p in sources:
    if not p.name.startswith("_"):
        all_tests.append(p)
    all_tests = sorted(all_tests)

class TestRunner(Renderer):
    def on_message(self, message, action):
        if action == "next_test":
            self.load_test(+1)
        elif action == "prev_test":
            self.load_test(-1)
        else:
            super().on_message(message, action)
    
    def load_test(self, inc):
        if hasattr(self, "test_index"):
            self.test_index += inc
        else:
            self.test_index = 0
        if self.test_index == -1:
            self.test_index = len(all_tests) - 1
        elif self.test_index == len(all_tests):
            self.test_index = 0
        
        test_path = all_tests[self.test_index]
        print("---" * 20)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>", test_path)
        self.reset_filepath(str(test_path))
        self.reload_and_render(Action.PreviewStoryboard)


def main():
    pargs, parser = Renderer.Argparser(name="pb.py", file=False, nargs=[["action", "read"], ["catalog", None]])
    TestRunner(parser).main()

if __name__ == "__main__":
    main()