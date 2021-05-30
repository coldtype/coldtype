from random import random

class SHLookup():
    def __init__(self, symbol, field):
        self.symbol = symbol
        self.field = field
        self.values = {}
    
    def get(self, k, default=None):
        if k in self.values:
            return self.values[k]
        else:
            return default
    
    def __getitem__(self, k):
        return self.values[k]
    
    def __len__(self):
        return len(self.values)
    
    def __repr__(self):
        if len(self) <= 5:
            return f"SHLookup(values:{self.values})"
        else:
            return f"SHLookup(count:{len(self.values)})"

    def record(self, ctx, key, values, cb):
        if isinstance(values, str):
            values = ctx.sh(values)
        else:
            values = [values]

        hide_all = False
        if key.startswith("Ƨ"):
            hide_all = True
            key = key[1:]
        
        keys = key.split("ƒ")
        if len(keys) > 1 and len(values) == 1:
            values = values[0]
        
        for idx, k in enumerate(key.split("ƒ")):
            value = values[idx]
            hide = False
            if k == "_":
                continue
            if k.startswith("_"):
                k = k[1:]
                hide = True
            if callable(value):
                value = value(ctx)
            
            if cb:
                res = cb(k, value)
                if res is False:
                    hide = True
            if not hide and not hide_all:
                self.values[k] = value
            setattr(self, k, value)
            #if cb:
            #    cb(k, value)

    def record_many(self, ctx, cb, *args, **kwargs):
        from coldtype.grid import Grid
        
        if len(args) > 0 and isinstance(args[0], Grid):
            kwargs = args[0].keyed
            args = []
        
        for arg in args:
            kwargs[str(random())] = arg
        
        for k, v in kwargs.items():
            self.record(ctx, k, v, cb)
        
        return self


class SHContext():
    def __init__(self):
        self.lookups = {}
        self.locals = {}
        self.subs = {}
    
    def __repr__(self):
        return f"SHContext({list(self.lookups.keys())})"
    
    def registered_lookup(self, symbol, lookup):
        lk = SHLookup(symbol, lookup)
        self.lookups[lookup] = lk
        setattr(self, lookup, lk)
        return lk
    
    def context_record(self, symbol, lookup, cb, *args, **kwargs):
        if not hasattr(self, lookup) or getattr(self, lookup) is None:
            self.registered_lookup(symbol, lookup)
        self.lookups[lookup].record_many(self, cb, *args, **kwargs)
        return self
    
    def sh(self, s):
        from coldtype.sh import sh
        return sh(s, self)