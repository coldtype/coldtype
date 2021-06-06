#!/usr/bin/env python
import os

from coldtype import *
from coldtype.renderer import Renderer
import glfw

all_tests = []

sources = list(Path("test/visuals").glob("test_*.py"))
sources.extend(list(Path("test/visuals").glob("test_*.md")))

for p in sources:
    if not p.name.startswith("_"):
        all_tests.append(p)
    all_tests = sorted(all_tests)

class TestRunner(Renderer):
    def before_start(self):
        if self.args.test:
            self.test_index = all_tests.index(Path(self.args.test))
        else:
            self.test_index = 0
        self.load_test(0, rerender=False)

    def on_message(self, message, action):
        if action == "next_test":
            self.load_test(+1)
        elif action == "prev_test":
            self.load_test(-1)
        else:
            super().on_message(message, action)
        
    def shortcuts(self):
        xs = super().shortcuts()
        xs["prev_test"] = [[[glfw.MOD_SUPER], glfw.KEY_B]]
        xs["next_test"] = [[[], glfw.KEY_N]]
        return xs
    
    def shortcut_to_action(self, shortcut):
        if shortcut == "prev_test":
            return self.load_test(-1)
        elif shortcut == "next_test":
            return self.load_test(+1)
        else:
            return super().shortcut_to_action(shortcut)
    
    def load_test(self, inc, rerender=True):
        self.test_index = cycle_idx(all_tests, self.test_index + inc)
        test_path = all_tests[self.test_index]
        print("---" * 20)
        print(">>>", test_path)
        self.reset_filepath(str(test_path))
        if rerender:
            self.reload_and_render(Action.PreviewStoryboard)
            self.set_title(str(test_path))
        return -1
    
    def restart(self):
        print("----------------------------")
        args = sys.argv
        test_path = str(all_tests[self.test_index])
        if len(args) > 1:
            args[-1] = test_path
        else:
            args.append(test_path)
        print(sys.executable, ["-m"]+args)
        os.execl(sys.executable, *(["-m"]+args))


def main():
    pargs, parser = Renderer.Argparser(name="pb.py", file=False, nargs=[["test", None]])
    TestRunner(parser).main()

if __name__ == "__main__":
    main()