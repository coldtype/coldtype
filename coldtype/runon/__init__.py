from coldtype import *

from typing import Callable, Optional
from inspect import signature
from random import Random


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


class Runon:
    def __init__(self,
        value=None,
        els=None,
        data=None,
        attrs=None,
        ):
        self._val = None
        self._els = els if els is not None else []
        
        self._visible = True
        self._alpha = 1

        self._attrs = attrs if attrs else {}
        self._data = data if data else {}
        self._parent = None

        self._tmp_attr_tag = None

        if value is not None:
            self._val = value

    # Array Operations

    def append(self, el):
        if callable(el):
            el = el(self)

        if isinstance(el, Runon):
            self._els.append(el)
        else:
            self._els.append(Runon(el))
        return self
    
    def insert(self, index, el):
        if callable(el):
            el = el(self)
        
        if el:
            self._els.insert(index, el)
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

    def __str__(self, data=False):
        return self.__repr__(data)
    
    def __repr__(self, data=False):
        return f"<{type(self).__name__}({self._val}/els={len(self)})/>"
    
    def __len__(self):
        return len(self._els)

    def __getitem__(self, index):
        return self._els[index]
        
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

    def map(self, fn: Callable[[int, "Runon"], Optional[DraftingPen]]):
        """Apply `fn` to all top-level pen(s) in this set;
        if `fn` returns a value, it will overwrite
        the pen it was given as an argument;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self._pens):
            res = _call_idx_fn(idx, p)
            if result:
                self._pens[idx] = result
        return self
    
    def mmap(self, fn: Callable[[int, DraftingPen], None]):
        """Apply `fn` to all top-level pen(s) in this set but
        do not look at return value; first m in mmap
        stands for `mutate`;
        fn lambda receives `idx, p` as arguments"""
        for idx, p in enumerate(self._pens):
            arg_count = len(inspect.signature(fn).parameters)
            if arg_count == 1:
                fn(p)
            else:
                fn(idx, p)
        return self
    
    def filter(self, fn: Callable[[int, DraftingPen], bool]):
        """Filter top-level pen(s)"""
        dps = self.multi_pen_class()
        for idx, p in enumerate(self._pens):
            if fn(idx, p):
                dps.append(p)
        #self._pens = dps._pens
        #return self
        return dps
    
    def pmap(self, fn):
        """Apply `fn` to all individal pens, recursively"""
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens"):
                p.pmap(fn)
            else:
                arg_count = len(inspect.signature(fn).parameters)
                if arg_count == 1:
                    res = fn(p)
                    if res is not None:
                        self[idx] = res
                else:
                    res = fn(idx, p)
                    if res is not None:
                        self[idx] = res
        return self
    
    def pfilter(self, fn):
        """Filter all pens, recursively"""
        to_keep = []
        for idx, p in enumerate(self._pens):
            if hasattr(p, "_pens"):
                matches = p.pfilter(fn)
                if len(matches) > 0:
                    to_keep.extend(matches)
            if fn(idx, p):
                to_keep.append(p)
        try:
            return type(self)(to_keep)
        except TypeError:
            return self.multi_pen_class(to_keep)
    
    def interpose(self, el_or_fn):
        new_pens = []
        for idx, el in enumerate(self._pens):
            if idx > 0:
                if callable(el_or_fn):
                    new_pens.append(el_or_fn(idx-1))
                else:
                    new_pens.append(el_or_fn.copy())
            new_pens.append(el)
        self._pens = new_pens
        return self
    
    def split(self, fn):
        out = self.multi_pen_class()
        curr = self.multi_pen_class()
        for pen in self:
            if fn(pen):
                out.append(curr)
                curr = self.multi_pen_class()
            else:
                curr.append(pen)
        out.append(curr)
        return out
    
    # Hierarchical Operations

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
            callback(self, 1, dict(depth=depth, alpha=alpha, idx=idx))
        else:
            utag = "_".join([str(i) for i in idx]) if idx else None
            callback(self, 0, dict(
                depth=depth, alpha=alpha, idx=idx, utag=utag))
        
        return self

    def collapse(self, levels=100, onself=False):
        """AKA `flatten` in some programming contexts, though
        `flatten` is a totally different function here that flattens outlines; this function flattens nested collections into one-dimensional collections"""
        els = []
        for el in self._els:
            if len(el) > 0 and levels > 0:
                els.extend(el.collapse(levels=levels-1)._els)
            else:
                els.append(el)
        
        out = type(self)(els=els)

        if onself:
            self._els = out._els
            return self
        else:
            return out
    
    def sum(self):
        r = self.collapse()
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
    
    def copy(self):
        # needs to copy the _val somehow...
        # simple hasattr?

        if hasattr(self._val, "copy"):
            v = self._val.copy()
        else:
            v = self._val

        _copy = type(self)(
            value=v,
            data=self._data.copy(),
            attrs=self._attrs.copy())
        
        for el in self._els:
            _copy.append(el.copy())
        
        return _copy
    
    # Data-access methods

    def attr(self,
        tag=None,
        field=None,
        recursive=True,
        **kwargs
        ):
        if tag is None:
            if self._tmp_attr_tag is not None:
                tag = self._tmp_attr_tag
            else:
                tag = "_default"
        
        if field: # getting, not setting
            return self._attrs.get(tag).get(field)

        attrs = self._attrs.get(tag, {})
        for k, v in kwargs.items():
            attrs[k] = v
        
        self._attrs[tag] = attrs

        if recursive:
            for el in self._els:
                print("helo")
                el.attr(tag=tag, field=None, recursive=True, **kwargs)
        
        return self
    
    def lattr(self, tag, fn):
        """temporarily change default tag to something other than 'default'"""
        self._tmp_attr_tag = tag
        fn(self)
        self._tmp_attr_tag = None
        return self
    
    def v(self, v):
        if callable(v):
            self.visible(bool(v(self)))
        else:
            self.visible(bool(v))
        return self
    
    def a(self, v):
        self._alpha = v
        return self