from typing import Callable, Optional
from inspect import signature
from random import Random
from time import sleep
from copy import deepcopy
from collections.abc import Iterable

from coldtype.fx.chainable import Chainable


def _arg_count(fn):
    return len(signature(fn).parameters)

def _call_idx_fn(fn, idx, arg):
    ac = _arg_count(fn)
    if ac == 1:
        return fn(arg)
    else:
        return fn(idx, arg)


class RunonException(Exception):
    pass


class RunonNoData:
    pass


class Runon:
    def __init__(self, *val):
        els = []

        if len(val) == 1 and not isinstance(val[0], Runon):
            if isinstance(val[0], Iterable):
                els = val[0]
                value = None
            else:
                value = val[0]
        else:
            value = None
            els = []
            for v in val:
                if isinstance(v, Runon):
                    els.append(v)
                else:
                    els.append(Runon(v))

        self._val = None
        self.reset_val()
        
        if value is not None:
            self._val = self.normalize_val(value)

        self._els = els
        
        self._visible = True
        self._alpha = 1

        self._attrs = {}
        self._data = {}
        self._parent = None
        self._tag = None

        self._tmp_attr_tag = None
    
    def post_init(self):
        """subclass hook"""
        pass

    # Value operations

    def update(self, val):
        if callable(val):
            val = val(self)
        
        self._val = val
        return self
    
    @property
    def v(self):
        return self._val

    # Array Operations

    def append(self, el):
        if callable(el):
            el = el(self)

        if isinstance(el, Runon):
            self._els.append(el)
        else:
            self._els.append(Runon(el))
        return self
    
    def extend(self, els):
        if callable(els):
            els = els(self)

        if isinstance(els, Runon):
            if len(els) > 0:
                self.append(els._els)
            else:
                self.append(els)
        else:
            [self.append(el) for el in els]
        return self
    
    # Generic Interface

    def __str__(self):
        return self.__repr__()
    
    def printable_val(self):
        """subclass hook for __repr__"""
        return self._val
    
    def printable_data(self):
        """subclass hook for __repr__"""
        return self._data
    
    def __repr__(self):
        v = self.printable_val()
        t = self._tag
        d = self.printable_data()
        l = len(self)

        if v is None:
            v = ""
        else:
            v = f"({v})"
        
        if l == 0:
            l = ""
        else:
            l = "/" + str(l) + "..."
        
        if t is None:
            t = ""
        else:
            t = f" {{#{t}}}"
        
        if len(d) == 0:
            d = ""
        else:
            d = " {" + ",".join([f"{k}={v}" for k,v in d.items()]) + "}"
        
        if self.val_present():
            tv = type(self._val).__name__
        else:
            tv = ""
        ty = type(self).__name__
        if ty == "Runon":
            ty = ""
        
        out = f"<®:{ty}:{tv}{v}{l}{t}{d}>"
        return out
    
    def __bool__(self):
        return len(self._els) > 0 or self._val is not None
    
    def val_present(self):
        """subclass hook"""
        return bool(self._val)
    
    def normalize_val(self, val):
        """subclass hook"""
        return val
    
    def reset_val(self):
        self._val = None
        return self
    
    def __len__(self):
        return len(self._els)

    def __getitem__(self, index):
        #try:
        return self._els[index]
        #except IndexError:
        #    return None
        
    def __setitem__(self, index, pen):
        self._els[index] = pen
    
    def __iadd__(self, el):
        return self.append(el)
    
    def __add__(self, el):
        return self.append(el)
    
    def tree(self, out=None, depth=0) -> str:
        """Hierarchical string representation"""
        if out is None:
            out = []
        out.append(" |"*depth + " " + str(self))
        for el in self._els:
            if len(el._els) > 0:
                el.tree(out=out, depth=depth+1)
            else:
                out.append(" |"*(depth+1) + " " + str(el))
        return "\n".join(out)
    
    def depth(self):
        if len(self) > 0:
            return 1 + max(p.depth() for p in self)
        else:
            return 1
    
    # Iteration operations

    def walk(self,
        callback:Callable[["Runon", int, dict], None],
        depth=0,
        visible_only=False,
        parent=None,
        alpha=1,
        idx=None
        ):
        if visible_only and not self._visible:
            return
        
        if parent:
            self._parent = parent
        
        alpha = self._alpha * alpha
        
        if len(self) > 0:
            callback(self, -1, dict(depth=depth, alpha=alpha, idx=idx))
            for pidx, el in enumerate(self._els):
                idxs = [*idx] if idx else []
                idxs.append(pidx)
                el.walk(callback, depth=depth+1, visible_only=visible_only, parent=self, alpha=alpha, idx=idxs)
            utag = "_".join([str(i) for i in idx]) if idx else None
            callback(self, 1, dict(depth=depth, alpha=alpha, idx=idx, utag=utag))
        else:
            #print("PARENT", idx)
            utag = "_".join([str(i) for i in idx]) if idx else None
            res = callback(self, 0, dict(
                depth=depth, alpha=alpha, idx=idx, utag=utag))
            
            if res is not None:
                parent[idx[-1]] = res
        
        return self

    def map(self, fn):
        for idx, p in enumerate(self._els):
            res = _call_idx_fn(fn, idx, p)
            if res:
                self._els[idx] = res
        return self
    
    def filter(self, fn):
        to_delete = []
        for idx, p in enumerate(self._els):
            res = _call_idx_fn(fn, idx, p)
            if res == False:
                to_delete.append(idx)
        to_delete = sorted(to_delete, reverse=True)
        for idx in to_delete:
            del self._els[idx]
        return self
    
    def mapv(self, fn):
        idx = 0
        def walker(el, pos, _):
            nonlocal idx
            if pos != 0: return
            
            res = _call_idx_fn(fn, idx, el)
            idx += 1
            return res
        
        return self.walk(walker)
    
    def filterv(self, fn):
        idx = 0
        def walker(el, pos, data):
            nonlocal idx
            
            if pos == 0:
                res = _call_idx_fn(fn, idx, el)
                if not res:
                    el.data(_walk_delete=True)
                idx += 1
                return None
            elif pos == 1:
                el.filter(lambda p: not p.data("_walk_delete"))
        
        return self.walk(walker)
    
    def unblank(self):
        return self.filterv(lambda p: p.v is not None)
    
    def interpose(self, el_or_fn):
        new_els = []
        for idx, el in enumerate(self._els):
            if idx > 0:
                if callable(el_or_fn):
                    new_els.append(el_or_fn(idx-1))
                else:
                    new_els.append(el_or_fn.copy())
            new_els.append(el)
        self._els = new_els
        return self
    
    # def interleave(self, style_fn, direction=-1, recursive=True):
    #     """Provide a callback-lambda to interleave new DATPens between the existing ones; useful for stroke-ing glyphs, since the stroked glyphs can be placed behind the primary filled glyphs."""
    #     els = []
    #     for idx, el in enumerate(self._els):
    #         if recursive:
    #             _p = p.interleave(style_fn, direction=direction, recursive=True)
    #             pens.append(_p)
    #         else:
    #             try:
    #                 np = style_fn(idx, p.copy())
    #             except TypeError:
    #                 np = style_fn(p.copy())
    #             if isinstance(np, self.single_pen_class):
    #                 np = [np]
    #             if direction < 0:
    #                 pens.extend(np)
    #             pens.append(p)
    #             if direction > 0:
    #                 pens.extend(np)

    #     self._pens = pens
    #     return self
    
    def split(self, fn, split=0):
        out = type(self)()
        curr = type(self)()

        for el in self._els:
            do_split = False
            if callable(fn):
                do_split = fn(el)
            else:
                if el._val == fn:
                    do_split = True
            
            if do_split:
                if split == -1:
                    curr.append(el)
                out.append(curr)
                curr = type(self)()
                if split == 1:
                    curr.append(el)
            else:
                curr.append(el)
        
        out.append(curr)
        self._els = out._els
        return self
    
    # Hierarchical Operations

    def collapse(self, levels=100):
        """AKA `flatten` in some programming contexts"""
        els = []
        for el in self._els:
            if el._val is not None:
                els.append(el)
            
            if len(el) > 0 and levels > 0:
                els.extend(el.collapse(levels=levels-1)._els)

        self._els = els
        return self
    
    def sum(self):
        r = self.copy().collapse()
        out = []
        for el in r:
            out.append(el._val)
        return out
    
    def reverse(self, recursive=False):
        """in-place element reversal"""
        self._els = list(reversed(self._els))
        if recursive:
            for el in self._els:
                el.reverse(recursive=True)
        return self
    
    def shuffle(self, seed=0):
        "in-place shuffle"
        r = Random()
        r.seed(seed)
        r.shuffle(self._els)
        return self
    
    def copy_val(self, val):
        if hasattr(val, "copy"):
            return val.copy()
        else:
            return val
    
    def copy(self, deep=True, with_data=True):
        """with_data is deprecated"""
        val_copy = self.copy_val(self._val)

        _copy = type(self)(val_copy)
        if deep:
            _copy._data = deepcopy(self._data)
            _copy._attrs = deepcopy(self._attrs)
        else:
            _copy._data = self._data.copy()
            _copy._attrs = self._attrs.copy()
        _copy._tag = self._tag
        
        for el in self._els:
            _copy.append(el.copy())
        
        return _copy
    
    def insert(self, idx, el):
        if callable(el):
            el = el(self)
        
        parent = self
        try:
            p = self
            for x in idx[:-1]:
                if len(self) > 0:
                    parent = p
                    p = p[x]
            
            p._els.insert(idx[-1], el)
            return self
        except TypeError:
            pass

        parent._els.insert(idx, el)
        return self
    
    def index(self, idx, fn=None):
        parent = self
        lidx = idx
        try:
            p = self
            for x in idx:
                if len(self) > 0:
                    parent = p
                    lidx = x
                    p = p[x]
                else:
                    return p.index(x, fn)
        except TypeError:
            p = self[idx]

        if fn:
            parent[lidx] = _call_idx_fn(fn, lidx, p)
        else:
            return parent[lidx]
        return self
    
    def indices(self, idxs, fn=None):
        out = []
        for idx in idxs:
            out.append(self.index(idx, fn))
        if fn is None:
            return out
        return self
    
    î = index
    ï = indices

    def find(self, finder_fn, fn=None):
        matches = []
        def finder(p, pos, _):
            found = False
            if pos >= 0:
                if isinstance(finder_fn, str):
                    found = p.tag() == finder_fn
                elif callable(finder_fn):
                    found = finder_fn(p)
                else:
                    found = all(p.data.get(k) == v for k, v in finder_fn.items())
            if found:
                if fn:
                    fn(p)
                else:
                    matches.append(p)
        
        self.walk(finder)
        if fn:
            return self
        else:
            return matches
    
    def find_(self, finder_fn):
        return self.find(finder_fn)[0]
    
    # Data-access methods

    def data(self, key=None, default=None, **kwargs):
        if key is None and len(kwargs) > 0:
            for k, v in kwargs.items():
                if callable(v):
                    v = _call_idx_fn(v, k, self)
                self._data[k] = v
            return self
        elif key is not None:
            return self._data.get(key, default)
        else:
            return self
    
    def tag(self, value=RunonNoData()):
        if isinstance(value, RunonNoData):
            return self._tag
        else:
            self._tag = value
            return self

    def style(self, style="_default"):
        if style and style in self._attrs:
            return self._attrs[style]
        else:
            return self._attrs.get("_default", {})

    def attr(self,
        tag=None,
        field=None,
        recursive=True,
        **kwargs
        ):

        if field is None and len(kwargs) == 0:
            field = tag
            tag = None

        if tag is None:
            if self._tmp_attr_tag is not None:
                tag = self._tmp_attr_tag
            else:
                tag = "_default"
        
        if field: # getting, not setting
            return self._attrs.get(tag, {}).get(field)

        attrs = self._attrs.get(tag, {})
        for k, v in kwargs.items():
            attrs[k] = v
        
        self._attrs[tag] = attrs

        if recursive:
            for el in self._els:
                el.attr(tag=tag, field=None, recursive=True, **kwargs)
        
        return self
    
    def lattr(self, tag, fn):
        """temporarily change default tag to something other than 'default'"""
        self._tmp_attr_tag = tag
        fn(self)
        self._tmp_attr_tag = None
        return self
    
    def _get_set_prop(self, prop, v, castfn=None):
        if v is None:
            return getattr(self, prop)

        _v = v
        if callable(v):
            _v = v(self)
        
        if castfn is not None:
            _v = castfn(_v)

        setattr(self, prop, _v)
        return self
    
    def visible(self, v=None):
        return self._get_set_prop("_visible", v, bool)
    
    def alpha(self, v=None):
        return self._get_set_prop("_alpha", v, float)
    
    # Logic Operations

    def cond(self, condition,
        if_true:Callable[["Runon"], None], 
        if_false:Callable[["Runon"], None]=None
        ):
        if callable(condition):
            condition = condition(self)

        if condition:
            if callable(if_true):
                if_true(self)
            else:
                #self.gs(if_true)
                pass # TODO?
        else:
            if if_false is not None:
                if callable(if_false):
                    if_false(self)
                else:
                    #self.gs(if_false)
                    pass # TODO?
        return self
    
    # Chaining

    def chain(self,
        fn:Callable[["Runon"], None],
        *args
        ):
        """
        For simple take-one callback functions in a chain
        """
        if fn:
            if isinstance(fn, Chainable):
                res = fn.func(self, *args)
                if res:
                    return res
                return self
            
            try:
                if isinstance(fn[0], Chainable):
                    r = self
                    for f in fn:
                        r = r.chain(f, *args)
                    return r
            except TypeError:
                pass

            try:
                fn, metadata = fn
            except TypeError:
                metadata = {}
            
            # So you can pass in a function
            # without calling it (if it has no args)
            # TODO what happens w/ no args but kwargs?
            ac = _arg_count(fn)
            if ac == 0:
                fn = fn()

            res = fn(self, *args)
            if "returns" in metadata:
                return res
            elif isinstance(res, Runon):
                return res
            elif res:
                return res
        return self
    
    ch = chain

    def layer(self, *layers):
        """
        For every lambda function you pass in, a copy of the original is made and passed to your function, building up a multi-layered version and removing the original version; alternatively,
        pass in an integer n to simply duplicate the
        current value of the pen n-times
        """
        if self.val_present():
            if len(layers) == 1 and isinstance(layers[0], int):
                layers = [1]*layers[0]
            
            els = []
            for layer in layers:
                if callable(layer):
                    els.append(layer(self.copy()))
                elif isinstance(layer, Chainable):
                    els.append(layer.func(self.copy()))
                #elif isinstance(layer, str):
                #    dp = self.copy()
                #    els.append(dp.sh("ctx" + layer)[0])
                else:
                    els.append(self.copy())
            
            self.reset_val()
            self.extend(els)
        else:
            for el in self._els:
                el.layer(*layers)
        
        return self
    
    # Utils

    def print(self, *args):
        if len(args) == 0:
            print(self.tree())
            return self

        for a in args:
            if callable(a):
                print(a(self))
            else:
                print(a)
        return self
    
    def noop(self, *args, **kwargs):
        """Does nothing"""
        return self
    
    def null(self):
        """For chaining; return an empty instead of this pen"""
        return self.single_pen_class()
    
    def _null(self):
        """For chaining; quickly disable a .null() call without a line-comment"""
        return self
    
    def sleep(self, time):
        """Sleep call within the chain (if you want to measure something)"""
        sleep(time)
        return self
    
    # Aliases

    pmap = mapv