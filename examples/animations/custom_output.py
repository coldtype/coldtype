from coldtype import *

class custom_output_animation(animation):
    def pass_path(self, index=0):
        return Path("custom_output_folder") / self.name / f"{self.pass_prefix()}{self.pass_suffix(index)}.{self.fmt}"

@custom_output_animation(bg=0)
def wght(f):
    return (StSt("CUSTOM\nOUTPUT", Font.MuSan(), 200, wght=f.e())
        .align(f.a.r)
        .f(1))
