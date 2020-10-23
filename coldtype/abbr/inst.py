from coldtype.pens.datpen import DATPen, DATPenSet, DATPenLikeObject
from coldtype.text.reader import StyledString, Style


class Inst():
    def __init__(self, *args):
        self.last = False
        self.immutable = False  
        self.instructions = [args]
    
    def __add__(self, inst):
        next_inst = inst.instructions[0][0]
        if next_inst == "pens":
            new_inst = Inst("pens")
            new_inst.instructions.append(self)
            new_inst.instructions.append(inst)
            return new_inst
        #print("__add__", self, self.immutable, self.instructions[0][0])
        if self.immutable:
            return self
        
        if isinstance(inst, Inst):
            if inst.last:
                self.immutable = True # refuse more
            
            if inst.immutable:
                self.immutable = True
            else:
                self.instructions.extend(inst.instructions)
        else:
            self.instructions.append(inst)
        return self

    def __sub__(self, next):
        # ignore
        return self
    
    def __truediv__(self, inst):
        print(self.instructions[0][0], inst.instructions[0][0])
        self.last = True
        inst.immutable = True
        #print("__truediv__", self, self.immutable, next)
        return self
    
    #def __str__(self):
    #    return f"<Inst({self.instructions[0][0]})/>"
    
    def print(self):
        for i in self.instructions:
            print(i)
    
    def realize(self):
        #from pprint import pprint
        #pprint(self.instructions)
        for idx, inst in enumerate(self.instructions):
            if idx > 0:
                if isinstance(inst, Inst):
                    self.instructions[idx] = inst.realize()

        if self.instructions[0][0] == "pen":
            return _build(DATPen, None, self.instructions[1:])
        elif self.instructions[0][0] == "pens":
            return _build(DATPenSet, None, self.instructions[1:])
        else:
            raise Exception("Cannot realize")


def _build(seed_class, seed, instructions):
    #print("BUILD", seed_class, seed, instructions)
    if isinstance(instructions, Inst):
        instructions = instructions.instructions

    if seed:
        dp = seed
    else:
        dp = seed_class()

    def realize_string():
        txt = dp["text"]
        if "style" in dp:
            fnt = dp["font"]
            props = dp["style"]
        elif "font" in dp:
            fnt = dp["font"]
            props = dict(fontSize=250)
        elif "font" not in dp:
            raise Exception("No font provided in abbr-string")
        
        stst = StyledString(txt, Style(fnt, **props))
        if seed_class == DATPen:
            return stst.pen()
        elif seed_class == DATPenSet:
            return stst.pens()
        else:
            raise Exception("WTF")

    for _args in instructions:
        if isinstance(_args, Inst):
            _args = _args.instructions
        else:
            try:
                _args = list(_args)
            except:
                pass
        #print(">>>", _args[0], "///", _args[1:])
        try:
            if _args[0] == "skip":
                continue
        except:
            pass

        try:
            for idx, arg in enumerate(_args[1:]):
                #print(">>>>>>>>>>>>.", idx, arg)
                if isinstance(arg, Inst):
                    _args[idx+1] = arg.realize()
                    #print(">>>>>>>>>>>>>>>", _args[idx])
        except:
            pass
        
        if not _args:
            continue
        elif isinstance(_args, StyledString): # TODO could be lazy?
            stst = _args
            if seed_class == DATPen:
                dp = stst.pen()
            elif seed_class == DATPenSet:
                dp = stst.pens()
        elif isinstance(_args, DATPen):
            if seed_class == DATPen:
                if len(dp) == 0:
                    dp = _args
                else:
                    dp.record(_args)
            else:
                dp.append(_args)
        elif isinstance(_args, DATPenSet):
            dp.append(_args)
        else:
            fn, *args = _args
            if isinstance(fn, DATPenLikeObject):
                dp.extend(_args)
            elif fn == "text":
                dp = dict(pen=dp, text=args[0])
            elif fn == "font":
                dp = dict(pen=dp.get("pen"), text=dp["text"], font=args[0]) # text, fontName
            elif fn == "style":
                dp = dict(pen=dp.get("pen"), text=dp["text"], font=dp["font"], style=args[0])
            else:
                # realize the string if it's still latent
                if isinstance(dp, dict):
                    pen = dp.get("pen")
                    dp = realize_string()
                    if pen and len(pen) > 0:
                        dp = DATPenSet([pen, dp])
                
                if fn == "wrap":
                    seed_class = DATPenSet
                    dp = DATPenSet([dp])
                elif fn == "subinstructions":
                    dp = _build(seed_class, dp, args)
                else:
                    try:
                        dp = getattr(dp, fn)(*args)
                    except Exception as e:
                        print("EXCEPTION--------------------")
                        print(fn, args)
                        print(e)
                        print("-----------------------------")
    
    if isinstance(dp, dict):
        pen = dp.get("pen")
        dp = realize_string()
        if pen:
            dp = DATPenSet([pen, dp])
    return dp