import re

from textwrap import wrap

from typing import Callable, Optional
from inspect import signature
from random import Random
from time import sleep
from copy import deepcopy
from collections.abc import Iterable
from collections import namedtuple
from functools import partial

from coldtype.fx.chainable import Chainable

_ARG_COUNT_CACHE = {}

def _arg_count(fn):
    if fn not in _ARG_COUNT_CACHE:
        count = len(signature(fn).parameters)
        _ARG_COUNT_CACHE[fn] = count
    return _ARG_COUNT_CACHE[fn]


RunonEnumerable = namedtuple("RunonEnumerable", ["i", "el", "e", "len", "k", "parent"])


class RunonException(Exception):
    pass


class RunonSearchException(Exception):
    pass


class RunonNoData:
    pass


class Runon:
    def __init__(self, *val):
        els = []
        to_append = []

        if len(val) == 1 and not isinstance(val[0], Runon):
            if isinstance(val[0], Iterable) and not isinstance(val[0], str):
                to_append = val[0]
                value = None
            else:
                value = val[0]
        else:
            value = None
            els = []
            to_append = val

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

        for el in to_append:
            self.append(el)
    
    def post_init(self):
        """subclass hook"""
        pass

    def yields_wrapped(self):
        """subclass hook"""
        return True

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

    def _call_idx_fn(self, fn, idx, arg:"Runon"):
        if not self.yields_wrapped():
            try:
                if arg.val_present():
                    arg = arg.v
            except AttributeError:
                arg = arg

        ac = _arg_count(fn)
        if ac == 1:
            return fn(arg)
        else:
            return fn(idx, arg)

    def _norm_element(self, el):
        if el is None:
            return None
        
        if callable(el):
            el = el(self)
        if not isinstance(el, Runon):
            el = type(self)(el)
        return el

    def append(self, el):
        el = self._norm_element(el)
        if el is None:
            return self
        if el.data("insert") is not None:
            self._els.insert(el.data("insert"), el)
            el.data(insert="delete")
        else:
            self._els.append(el)
        return self

    å = append
    
    def replicate(self, *els):
        for el in els:
            self.append(el.copy())
        return self
    
    def attach(self, parent):
        parent.append(self)
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
    
    def insert(self, idx, el):
        el = self._norm_element(el)
        
        if el is None:
            return self
        
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
    
    def __iadd__(self, item):
        """alias to append"""
        return self.append(item)
    
    def __add__(self, item):
        """yields new Runon with current nested, item after"""
        return type(self)(self, item)
    
    # Generic Interface

    def __str__(self):
        return self.__repr__()
    
    def printable_val(self):
        """subclass hook for __repr__"""
        return self._val
    
    def printable_data(self):
        """subclass hook for __repr__"""
        return self._data
    
    def __repr__(self, **kwargs):
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
            if True:
                ds = []
                for k, _v in d.items():
                    if len(kwargs) == 0 or kwargs.get(k, True):
                        ds.append(f"{k}={_v}")
                d = " {" + ",".join(ds) + "}"
            else:
                d = " {" + ",".join([f"{k}={v}" for k,v in d.items()]) + "}"
        
        if self.val_present():
            tv = type(self._val).__name__
            #if len(tv) > 5:
            #    tv = tv[:5] + "..."
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
        return self._val is not None
    
    def normalize_val(self, val):
        """subclass hook"""
        return val
    
    def reset_val(self):
        self._val = None
        self._data = {}
        self._attrs = {}
        self._tag = None
        return self
    
    def __len__(self):
        return len(self._els)

    def __getitem__(self, index):
        if isinstance(index, int) or isinstance(index, slice):
            el = self._els[index]
        else:
            tag = index
            el = self.find_(tag)
        
        if el and self.data("vend"):
            return el.copy()
        
        return el
    
    def get(self, key, default=None):
        try:
            return self[key]
        except RunonSearchException:
            return default

    
    def subset(self, *idxs):
        """return subset of self wrapped in same type as self (rather than raw list)"""
        if isinstance(idxs[0], slice):
            return type(self)(self._els[idxs[0]])
        else:
            out = type(self)()
            for i in idxs:
                out.append(self[i%len(self._els)])
            return out
        
    def __setitem__(self, index, pen):
        self._els[index] = pen
    
    def tree(self, v=True, limit=100, **kwargs):
        out = []
        def walker(el, pos, data):
            if pos <= 0:
                if pos == 0 and not v:
                    return
                
                dep = data.get("depth", 0)
                tab = " |"*dep
                if pos == 0:
                    tab = tab[:-1] + "-"
                
                sel = el.__repr__(**kwargs)
                sel = wrap(sel, limit, initial_indent="", subsequent_indent="  "*(dep+2) + " ")
                out.append(tab + " " + "\n".join(sel))
        
        self.walk(walker)
        return "\n" + "\n".join(out)
    
    def depth(self):
        if len(self) > 0:
            return 1 + max(p.depth() for p in self)
        else:
            return 0
    
    # Iteration operations

    def walk(self,
        callback:Callable[["Runon", int, dict], None],
        depth=0,
        visible_only=False,
        parent=None,
        alpha=1,
        idx=None,
        _selector=None,
        ):
        if visible_only and not self._visible:
            return
        
        if parent:
            self._parent = parent
        
        alpha = self._alpha * alpha
        
        if len(self) > 0:
            utag = "_".join([str(i) for i in idx]) if idx else None
            if utag is None and parent is None:
                utag = "ROOT"
            if _selector is None or _selector == -1:
                callback(self, -1, dict(depth=depth, alpha=alpha, idx=idx, utag=utag))
            
            for pidx, el in enumerate(self._els):
                idxs = [*idx] if idx else []
                idxs.append(pidx)
                el.walk(callback, depth=depth+1, visible_only=visible_only,
                    parent=self, alpha=alpha, idx=idxs, _selector=_selector)
            
            utag = "_".join([str(i) for i in idx]) if idx else None
            if utag is None and parent is None:
                utag = "ROOT"
            if _selector is None or _selector == +1:
                callback(self, 1, dict(depth=depth, alpha=alpha, idx=idx, utag=utag))
        else:
            utag = "_".join([str(i) for i in idx]) if idx else None
            if utag is None and parent is None:
                utag = "ROOT"
            
            res = callback(self, 0, dict(
                depth=depth, alpha=alpha, idx=idx, utag=utag))
            
            if res is not None:
                if parent is None:
                    return res
                else:
                    parent[idx[-1]] = res
        
        return self
    
    def prewalk(self, callback):
        return self.walk(callback, _selector=-1)
    
    def postwalk(self, callback):
        return self.walk(callback, _selector=+1)
    
    def parent(self, noexist_ok=False):
        if self._parent:
            return self._parent
        else:
            if not noexist_ok:
                print("no parent set")
            return None
        
    def match(self, regex, cb=None, partial=False):
        matches = []
        rek = re.compile(regex)

        def walker(el, _, __):
            p = el.path(self)
            if partial:
                m = rek.match(p)
            else:
                m = rek.fullmatch(p)
            
            if m:
                if cb:
                    cb(el)
                else:
                    matches.append(el)
            
        self.prewalk(walker)
        
        if not cb:
            return matches
        else:
            return self

    def map(self, fn, range=None):
        els = self._els[range] if range is not None else self._els
        for idx, p in enumerate(els):
            res = self._call_idx_fn(fn, idx, p)
            if res:
                self._els[idx] = res
        return self
    
    def mape(self, fn):
        total = len(self._els)
        for idx, p in enumerate(self._els):
            res = fn(idx/(total-1), p)
            if res:
                self._els[idx] = res
        return self
    
    def filter(self, fn):
        to_delete = []
        for idx, p in enumerate(self._els):
            if isinstance(fn, str):
                res = p.tag() == fn
            else:
                res = self._call_idx_fn(fn, idx, p)
            if res == False:
                to_delete.append(idx)
        to_delete = sorted(to_delete, reverse=True)
        for idx in to_delete:
            del self._els[idx]
        return self
    
    def remove(self, fn):
        to_delete = []
        for idx, p in enumerate(self._els):
            if isinstance(fn, str):
                res = p.tag() == fn
            else:
                res = self._call_idx_fn(fn, idx, p)
            if res == True:
                to_delete.append(idx)
        to_delete = sorted(to_delete, reverse=True)
        for idx in to_delete:
            del self._els[idx]
        return self
    
    def mapv(self, fn):
        if len(self) == 0:
            if self.val_present():
                print("! no els to mapv")
            return self

        idx = 0
        def walker(el, pos, _):
            nonlocal idx
            if pos != 0: return
            
            res = self._call_idx_fn(fn, idx, el)
            idx += 1
            return res
        
        return self.walk(walker)
    
    def mapvrc(self, fn:Callable[[int, int, "Runon"], "Runon"]):
        """
        (map)-(v)alues with (r)ow-and-(c)olumn
        __only works with spread/stack structure__
        """
        def walker(p, pos, data:dict):
            if pos == 0:
                r, c = data.get("idx", (-1, -1))
                return fn(r, c, p)

        return self.walk(walker)
    
    def mapvch(self, fn:Callable[[bool, "Runon"], "Runon"]):
        """
        (map)-(v)alues (ch)eckerboard style
        """
        return self.mapvrc(lambda r, c, p: fn(not((not r%2 and not c%2) or (r%2 and c%2)), p))
    
    def filterv(self, fn):
        idx = 0
        def walker(el, pos, data):
            nonlocal idx
            
            if pos == 0:
                res = self._call_idx_fn(fn, idx, el)
                if not res:
                    el.data(_walk_delete=True)
                idx += 1
                return None
            elif pos == 1:
                el.filter(lambda p: not p.data("_walk_delete"))
        
        return self.walk(walker)
    
    def delete(self):
        self._els = []
        self.reset_val()
        return self
    
    def deblank(self):
        return self.filterv(lambda p: p.val_present())
    
    removeBlanks = deblank
    
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
    
    def enumerate(self, enumerable, enumerator):
        es = list(enumerable)
        length = len(es)

        if length == 0:
            return self

        if isinstance(enumerable, dict):
            for idx, k in enumerate(enumerable.keys()):
                item = enumerable[k]
                if idx == 0 and len(enumerable) == 1:
                    e = 0.5
                else:
                    e = idx / (length-1)
                result = enumerator(RunonEnumerable(idx, item, e, length, k, self))
                if result != self:
                    self.append(result)
        else:
            for idx, item in enumerate(es):
                if idx == 0 and length == 1:
                    e = 0.5
                else:
                    e = idx / (length-1)
                
                result = enumerator(RunonEnumerable(idx, item, e, length, idx, self))
                if result != self:
                    self.append(result)
        return self
    
    # Hierarchical Operations

    def collapse(self, deblank=True):
        """AKA `flatten` in some programming contexts"""
        els = []
        def walk(el, pos, data):
            if pos == 0 and (el.val_present() or not deblank):
                els.append(el)
        
        self.walk(walk)
        self._els = els
        return self
    
    def collapseonce(self, deblank=True):
        """Same as collapse, except only collapses one-level"""
        els = []

        for el in self._els:
            els.extend(el._els)

        self._els = els
        return self
    
    def sum(self):
        out = []
        if self.val_present():
            out.append(self._val)
        
        r = self.copy().collapse()
        for el in r._els:
            out.append(el._val)
        return out
    
    def reverse(self, recursive=False, winding=True):
        """in-place element reversal"""
        self._els = list(reversed(self._els))
        if recursive:
            for el in self._els:
                el.reverse(recursive=True, winding=winding)
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
        copied = False
        
        if deep:
            try:
                _copy._data = deepcopy(self._data)
                _copy._attrs = deepcopy(self._attrs)
                copied = True
            except TypeError:
                pass
        
        if not copied:
            _copy._data = self._data.copy()
            _copy._attrs = self._attrs.copy()
        
        _copy._tag = self._tag

        # kind of a hack but necessary
        if hasattr(self, "_stst"):
            _copy._stst = self._stst
        
        for el in self._els:
            _copy.append(el.copy())
        
        return _copy
    
    def index(self, idx, fn=None):
        parent = self
        lidx = idx

        try:
            p = self
            for x in idx:
                if len(p) > 0:
                    parent = p
                    lidx = x
                    p = p[x]
                else:
                    res = p.index(x, fn)
                    if not fn:
                        return res
                    else:
                        return self
        except TypeError as e:
            try:
                p = self[idx]
            except IndexError:
                return self

        if fn:
            res = self._call_idx_fn(fn, lidx, p)
            if res is not None:
                parent[lidx] = res
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
    
    def î(self, idx, fn=None):
        return self.index(idx, fn)

    def ï(self, idxs, fn=None):
        return self.indices(idxs, fn)

    def find(self,
        finder_fn,
        fn=None,
        index=None,
        find_one=False,
        ):
        matches = []
        found_one = []

        def finder(p, pos, data):
            if len(found_one) > 0:
                return
            #if limit and len(matches) > limit:
            #    return

            found = False
            if pos <= 0 and data["depth"] > 0:
                if isinstance(finder_fn, str):
                    found = p.tag() == finder_fn
                elif callable(finder_fn):
                    found = finder_fn(p)
                else:
                    found = all(p.data(k) == v for k, v in finder_fn.items())
            
            if found:
                matches.append([p, data["depth"]])
                if find_one:
                    found_one.append(True)

        self.walk(finder)

        #matches = list(reversed(sorted(matches, key=lambda m: m.depth())))

        matches = list([m[0] for m in sorted(matches, key=lambda m: m[1])])

        narrowed = []
        if index is not None:
            for idx, match in enumerate(matches):
                if isinstance(index, int):
                    if idx == index:
                        narrowed.append([idx, match])
                else:
                    if idx in index:
                        narrowed.append([idx, match])
        else:
            for idx, match in enumerate(matches):
                narrowed.append([idx, match])
        
        if fn:
            for idx, match in narrowed:
                self._call_idx_fn(fn, idx, match)

        if fn:
            return self
        else:
            return [m for (_, m) in narrowed]
    
    def find_(self, finder_fn=None, fn=None, index=0, none_ok=0, find_one=False, **kwargs):
        if len(kwargs) > 0 and finder_fn is None:
            finder_fn = kwargs

        if isinstance(finder_fn, str):
            if "+" in finder_fn:
                finders = finder_fn.split("+")
                parts = []
                for finder in finders:
                    parts.append(self.find_(finder, none_ok=1))
                return type(self)([p for p in parts if p])
            elif "/" in finder_fn:
                o = self
                for k in finder_fn.split("/"):
                    if k == "<":
                        o = self.parent()
                        continue
                    o = o.find_(k)
                return o

        res = self.find(finder_fn, fn, index=index, find_one=find_one)
        if not fn:
            try:
                return res[0]
            except IndexError:
                if none_ok:
                    return None
                raise RunonSearchException(f"Could not find `{finder_fn}`")
        else:
            return self
        
    def replace(self, tag, replacement, limit=None):
        if isinstance(tag, str):
            def walker(p, pos, data):
                if pos in [0, 1]:
                    if p.tag() == tag:
                        self.index(data["idx"], replacement)
            return self.walk(walker)
        elif callable(tag):
            def walker(p, pos, data):
                if pos in [0, 1]:
                    if tag(p):
                        self.index(data["idx"], replacement)
            return self.walk(walker)
        else:
            raise Exception("not yet supported")
        
    def swap(self, indices, replace_fn):
        def _replace_fn(p):
            pc = p.copy()
            p.delete()
            p.up()
            p.append(replace_fn(pc))
        
        return self.index(indices, _replace_fn)
    
    def partition(self, fn):
        last = None
        group = type(self)()
        out = type(self)()
        for p in self:
            v = fn(p)
            if last == v:
                group.append(p)
            else:
                if len(group) > 0:
                    out.append(group)
                    group = type(self)()
                group.append(p)
            last = v
        out.append(group)
        return out
    
    # Data-access methods

    def data(self, key=None, default=None, function_literals=False, **kwargs):
        """Set with kwargs, read with key= & default="""
        if key is None and len(kwargs) > 0:
            for k, v in kwargs.items():
                if v == "delete":
                    del self._data[k]
                else:
                    if not function_literals and callable(v):
                        v = self._call_idx_fn(v, k, self)
                    self._data[k] = v
            return self
        elif key is None and kwargs is not None:
            return self
        elif key is not None:
            return self._data.get(key, default)
        else:
            return self._data
    
    def datafn(self, **kwargs):
        """Set function literals with kwargs"""
        return self.data(function_literals=True, **kwargs)
    
    def tag(self, value=RunonNoData()):
        if isinstance(value, RunonNoData):
            return self._tag
        else:
            self._tag = value
            return self
    
    def path(self, root=None):
        tags = [self.tag()]
        parent = self.parent(noexist_ok=True)
        while parent and parent != root:
            tags.insert(0, parent.tag())
            parent = parent.parent(noexist_ok=True)
        return "/".join([t for t in tags if t])

    def style(self, style="_default"):
        if style and style in self._attrs:
            return self._attrs[style]
        else:
            return self._attrs.get("_default", {})
    
    def styles(self):
        all = {}
        for k, _ in self._attrs.items():
            style = self.style(k)
            if k == "_default":
                all["default"] = style
            else:
                all[k] = style
        return all
    
    @property # deprecated / backwards-compatibility
    def attrs(self):
        return self.styles()
    
    def normalize_attr_value(self, k, v):
        """subclass hook"""
        return v

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
        
        if tag == "default":
            tag = "_default"
        
        if field: # getting, not setting
            return self._attrs.get(tag, {}).get(field)

        attrs = self._attrs.get(tag, {})
        for k, v in kwargs.items():
            attrs[k] = self.normalize_attr_value(k, v)
        
        self._attrs[tag] = attrs

        if recursive:
            for el in self._els:
                el.attr(tag=tag, field=None, recursive=True, **kwargs)
        
        return self
    
    def cast(self, _class, *args):
        """Quickly cast to a (different) subclass."""
        res = _class(self, *args)
        res._attrs = deepcopy(self._attrs)
        return res
    
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
    
    def hide(self, *indices):
        if len(indices) > 0:
            for idx in indices:
                self.index(idx, lambda p: p.visible(False))
        else:
            self.visible(False)
        
        if self.val_present():
            self.visible(False)
        
        return self
    
    def __neg__(self):
        return self.hide()
    
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
    
    def attempt(self, exception_class, try_fn, except_fn):
        try:
            try_fn(self)
        except exception_class:
            except_fn(self)
    
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

    def __or__(self, other):
        return self.chain(other)

    def __ror__(self, other):
        return self.chain(other)
    
    def __truediv__(self, other):
        return self.mapv(other)
    
    def __sub__(self, other):
        """noop"""
        return self

    def up(self):
        """up one level of hierarchy"""
        copy = self.copy()

        self.reset_val()

        self._els = [copy]
        return self
    
    ups = up

    def down(self):
        """down one level of hierarchy — unimplemented by Runon"""
        return self
    
    def replicate(self, cells, mod=None):
        return (type(self)().enumerate(cells, lambda x: self.copy().align(x.el).ch(partial(mod, x.el) if mod else None)))

    def layer(self, *layers):
        if len(layers) == 1 and isinstance(layers[0], int):
            layers = [1]*layers[0]
        
        els = []

        for layer in layers:
            try:
                c = layer[0]
                for x in range(0, c):
                    els.append(layer[1](x, self.copy()))
            except TypeError:
                if callable(layer):
                    els.append(layer(self.copy()))
                elif isinstance(layer, Chainable):
                    els.append(layer.func(self.copy()))
                else:
                    els.append(self.copy())
        
        self.reset_val()
        self._els = els
        return self

    def layerv(self, *layers):
        if self.val_present():
            if len(layers) == 1 and isinstance(layers[0], int):
                layers = [1]*layers[0]
            
            els = []
            for layer in layers:
                if callable(layer):
                    els.append(layer(self.copy()))
                elif isinstance(layer, Chainable):
                    els.append(layer.func(self.copy()))
                else:
                    els.append(self.copy())
            
            self.reset_val()
            self.extend(els)
        else:
            for el in self._els:
                el.layerv(*layers)
        
        return self
    
    def overwrite(self, fn):
        self.layer(fn)
        return self[0]
    
    # Utils

    def declare(self, *whatever):
        # TODO do something with what's declared somehow?
        return self

    def print(self, *args, **kwargs):
        if len(args) == 0:
            print(self.tree(**kwargs))
            return self

        out = []
        for a in args:
            if callable(a):
                out.append(str(a(self)))
            else:
                out.append(str(a))
        print(" ".join(out))
        return self
    
    def pprint(self, *args):
        if len(args) == 0:
            print(self.tree())
            return self
        
        from pprint import pprint
        for a in args:
            if callable(a):
                pprint(a(self))
            else:
                pprint(a)
        return self
    
    def printh(self):
        """print hierarchy, no values"""
        print(self.tree(v=False))
        return self
    
    def printdata(self, field):
        print(self.data(field))
        return self
    
    def noop(self, *args, **kwargs):
        """Does nothing"""
        return self
    
    def null(self):
        """For chaining; return an empty instead of this pen"""
        self.reset_val()
        self._els = []
        return self
    
    def sleep(self, time):
        """Sleep call within the chain (if you want to measure something)"""
        sleep(time)
        return self
    
    # Aliases

    pmap = mapv