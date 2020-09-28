from coldtype import *
from coldtype.renderer import Renderer

all_tests = []
for p in Path("test").glob("test_*.py"):
    all_tests.append(p)

class TestRunner(Renderer):
    def on_message(self, message, action):
        if action == "next_test":
            if hasattr(self, "test_index"):
                self.test_index += 1
            else:
                self.test_index = 0
            test_path = all_tests[self.test_index]
            print("---" * 20)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>", test_path)
            self.reset_filepath(str(test_path))
            self.reload_and_render(Action.PreviewStoryboard)
        else:
            super().on_message(message, action)

def main():
    pargs, parser = Renderer.Argparser(name="pb.py", file=False, nargs=[["action", "read"], ["catalog", None]])
    TestRunner(parser).main()

if __name__ == "__main__":
    main()