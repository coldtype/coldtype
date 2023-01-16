import re, os
from pathlib import Path
from runpy import run_path
from functools import partial
from tempfile import NamedTemporaryFile
from subprocess import run
from typing import Union
from coldtype.blender import BlenderIO

from coldtype.renderable import renderable, ColdtypeCeaseConfigException, runnable, animation, aframe, ui

from coldtype.renderer.utils import Watchable, on_linux, on_mac, on_windows
from coldtype.renderer.config import ColdtypeConfig
from coldtype.helpers import sibling
from coldtype.text.reader import ALL_FONT_DIRS
from coldtype.geometry.rect import Rect
from coldtype.timing import Timeline
from coldtype.timing.viewer import timeViewer

try:
    from docutils.core import publish_doctree
except ImportError:
    publish_doctree = None


def apply_syntax_mods(filepath, source_code, renderer=None):
    codepath_offset = 0

    def inline_arg(p):
        path = Path(inline.strip()).expanduser().absolute()
        if renderer:
            if path not in renderer.watchee_paths():
                renderer.add_watchee([Watchable.Source, path, None])
        src = path.read_text()
        codepath_offset = len(src.split("\n"))
        return src
    
    def inline_other(x):
        cwd = Path.cwd()
        m = x.group(1)
        if m.startswith("."):
            path = filepath.parent / (m[1:] + ".py")
        else:
            path = Path(cwd / (m.replace(".", "/")+".py"))
        if renderer:
            if path not in renderer.watchee_paths():
                renderer.add_watchee([Watchable.Source, path, None])
        src = path.read_text()
        codepath_offset = len(src.split("\n"))
        return src

    if renderer and renderer.source_reader.config.inline_files:
        for inline in renderer.source_reader.config.inline_files:
            source_code = inline_arg(inline) + "\n" + source_code

    source_code = re.sub(r"from ([^\s]+) import \* \#INLINE", inline_other, source_code)
    #source_code = re.sub(r"ℛ", "return ", source_code)
    #source_code = re.sub(r"\-\.[A-Za-z_ƒ]+([A-Za-z_0-9]+)?\(", ".nerp(", source_code)
    #source_code = re.sub(r"([\s]+)Ƨ\(", r"\1nerp(", source_code)
    #source_code = re.sub(r"λ[\s]{0,3}\.", "lambda p: p.", source_code)
    #source_code = re.sub(r"λ\s?([/\.\@]{1,2})", r"lambda xxx: xxx\1", source_code)
    #source_code = re.sub(r"ι,λ\.", "lambda ι, λ__: λ__.", source_code)
    source_code = re.sub(r"λ(\s+)?\.", "lambda λ__: λ__.", source_code)
    source_code = re.sub(r"λ__", "λ", source_code)
    #source_code = re.sub(r"λ", "lambda ", source_code)
    #source_code = re.sub(r"ßDPS\(([^\)]+)\)", r"(ß:=P(\1))", source_code)

    # while "nerp(" in source_code:
    #     start = source_code.find("nerp(")
    #     end = -1
    #     i = 5
    #     depth = 1
    #     c = source_code[start+i]
    #     while depth > 0 and c:
    #         #print(c, depth)
    #         if c == "(":
    #             depth += 1
    #         elif c== ")":
    #             depth -= 1
    #         i += 1
    #         c = source_code[start+i]
    #     end = start+i
    #     source_code = source_code[:start] + "noop()" + source_code[end:]
    #     #print(start, end)
    
    if renderer:
        renderer._codepath_offset = codepath_offset
    
    return source_code, codepath_offset


def read_source_to_tempfile(filepath:Path,
    codepath:Path=None,
    renderer=None
    ):
    data_out = {}

    if filepath.suffix == ".rst":
        if not publish_doctree:
            raise Exception("pip install docutils")
        doctree = publish_doctree(filepath.read_text())
        def is_code_block(node):
            if node.tagname == "literal_block":
                classes = node.attributes["classes"]
                # ok the "ruby" here is an ugly hack but it's so I can hide certain code
                # from a printed rst
                if "code" in classes and ("python" in classes or "ruby" in classes):
                    return True
            return False
        code_blocks = doctree.traverse(condition=is_code_block)
        source_code = [block.astext() for block in code_blocks]
        if codepath and codepath.exists():
            codepath.unlink()
        with NamedTemporaryFile("w", prefix="coldtype_rst_src", suffix=".py", delete=False) as tf:
            tf.write("\n".join(source_code))
            codepath = Path(tf.name)
    
    elif filepath.suffix == ".md":
        from lxml.html import fragment_fromstring, tostring
        try:
            import markdown
        except ImportError:
            raise Exception("pip install markdown")
        try:
            import frontmatter
        except ImportError:
            frontmatter = None
            print("> pip install python-frontmatter")
        md = markdown.markdown(filepath.read_text(),
            extensions=["fenced_code"])
        fm = frontmatter.loads(filepath.read_text())
        data_out["frontmatter"] = fm
        frag = fragment_fromstring(md, create_parent=True)
        blocks = []
        for python in frag.findall("./pre/code[@class='language-python']"):
            blocks.append(python.text)
        source_code = "\n".join(blocks)
        if codepath and codepath.exists():
            codepath.unlink()
        with NamedTemporaryFile("w", prefix="coldtype_md_src", suffix=".py", delete=False) as tf:
            mod_src, _ = apply_syntax_mods(filepath, source_code, renderer)
            tf.write(mod_src)
            codepath = Path(tf.name)
    
    elif filepath.suffix == ".py":
        source_code, _ = apply_syntax_mods(filepath, filepath.read_text(), renderer)
        if codepath and codepath.exists():
            codepath.unlink()
        with NamedTemporaryFile("w", prefix=f"coldtype__{filepath.stem}_", suffix=".py", delete=False) as tf:
            tf.write(source_code)
            codepath = Path(tf.name)
    else:
        raise Exception("No code found in file!")
    
    return codepath, data_out


def run_source(filepath, codepath, inputs, memory, **kwargs):
    return run_path(str(codepath), init_globals={
        "__COLDTYPE__": True,
        "__FILE__": filepath,
        "__inputs__": inputs,
        "__memory__": memory,
        "__as_config__": False,
        "__sibling__": partial(sibling, filepath),
        **kwargs})


def renderable_to_output_folder(filepath, renderable, override=None):
    if override:
        return Path(override).expanduser().resolve()
    elif renderable.dst:
        return renderable.dst / (renderable.custom_folder or renderable.folder(filepath))
    else:
        return (filepath.parent if filepath else Path(os.getcwd())) / "renders" / (renderable.custom_folder or renderable.folder(filepath))


def find_renderables(
    filepath:Path,
    codepath:Path,
    program:dict,
    output_folder_override=None,
    blender_io=None,
    args=None,
    ):
    all_rs = []
    filtered_rs = []
    
    for k, v in program.items():
        if (isinstance(v, renderable) or isinstance(v, runnable)) and not v.hidden:
            if v.cond is not None:
                if callable(v.cond) and not v.cond():
                    continue
                elif not v.cond:
                    continue
            
            if v not in all_rs:
                all_rs.append(v)
        
        elif k == "RENDERABLES":
            for r in v:
                all_rs.append(r)
    
    #all_rs = sorted(all_rs, key=lambda r: r.layer)
    all_rs = sorted(all_rs, key=lambda r: r.sort)

    for r in all_rs:
        r.filepath = filepath
        r.codepath = codepath
        r.output_folder = renderable_to_output_folder(
            filepath, r, override=output_folder_override)

        if hasattr(r, "blender_io"):
            r.blender_io = blender_io

        r.post_read()

    if any([r.solo for r in all_rs]):
        filtered_rs = [r for r in all_rs if r.solo]
    else:
        filtered_rs = all_rs
    
    return filtered_rs


def filter_renderables(filtered_rs,
    viewer_solos=[],
    function_filters=[],
    class_filters=[],
    previewing=False,
    ):
        
    if function_filters:
        function_patterns = function_filters
        matches = []
        for r in filtered_rs:
            for fp in function_patterns:
                try:
                    if re.search(fp, r.name) and r not in matches:
                        matches.append(r)
                except re.error as e:
                    print("ff regex compilation error", e)
        if len(matches) > 0:
            filtered_rs = matches
    
    if class_filters:
        matches = []
        for r in filtered_rs:
            for cf in class_filters:
                try:
                    if re.match(cf, r.__class__.__name__) and r not in matches:
                        matches.append(r)
                except re.error as e:
                    print("cf regex compilation error", e)
        filtered_rs = matches
    
    if previewing:
        matches = []
        for r in filtered_rs:
            if not r.render_only:
                matches.append(r)
        filtered_rs = matches
    
    if len(viewer_solos) > 0:
        viewer_solos = [vs%len(filtered_rs) for vs in viewer_solos]

        solos = []
        for i, r in enumerate(filtered_rs):
            if i in viewer_solos:
                solos.append(r)
        filtered_rs = solos
    
    return filtered_rs


class SourceReader():
    def __init__(self,
        filepath:Path=None,
        code:str=None,
        renderer=None,
        runner:str="default",
        inputs=None,
        cli_args=None,
        use_blender=False,
        ):
        self.filepath = None
        self.codepath = None
        self.data_out = None
        self.dirpath = None
        self.should_unlink = False
        self.program = None
        self.candidates = None
        self.renderer = renderer
        self.runner = runner
        self.inputs = inputs or []
        self.use_blender = use_blender

        self.config = None
        self.read_configs(cli_args, filepath)

        if filepath or code:
            self.reset_filepath(filepath, code)
    
    @staticmethod
    def Script(name):
        root = Path(__file__).parent.parent
        if name.startswith("script:"):
            script = root / (name.replace(":", "s/") + ".py")
            if script.exists():
                return script
        return False

    @staticmethod
    def Demo(name):
        root = Path(__file__).parent.parent
        if not name:
            return root / "demo/demo.py"
        elif name == "demo":
            return root / "demo/demo.py"
        elif name == "blank":
            return root / "demo/blank.py"
        elif name == "boiler":
            return root / "demo/boiler.py"
        elif name == "glyphloop" or name == "gl":
            return root / "demo/glyphloop.py"
        elif name == "glyphs" or name == "g":
            return root / "demo/glyphs.py"
        elif name == "midi":
            return root / "demo/midi.py"
        elif name == "vf":
            return root / "demo/vf.py"
        elif name == "viewseq":
            return root / "demo/viewseq.py"
        elif name == "docstrings":
            return root / "demo/docstrings.py"
        return name
    
    @staticmethod
    def LoadDemo(demoname, **inputs):
        return SourceReader(
            SourceReader.Demo(demoname),
            inputs=inputs).renderables()
    
    @staticmethod
    def FrameResult(name, frame, inputs={}, renderer_state=None):
        filepath = SourceReader.Demo(name)
        sr = SourceReader(filepath, inputs=inputs)
        sr.unlink()
        return sr.frame_results(frame,
            renderer_state=renderer_state)
    
    def read_configs(self, args, filepath):
        embedded = Path(__file__).parent / ".coldtype.py"
        proj = Path(".coldtype.py")
        user = Path("~/.coldtype.py").expanduser()
        
        if on_windows():
            os = Path(".coldtype.win.py")
        elif on_mac():
            os = Path(".coldtype.mac.py")
        elif on_linux():
            os = Path(".coldtype.lin.py")

        files = [embedded, user, proj, os]

        if args and hasattr(args, "config") and args.config:
            if args.config == "0":
                files = []
            else:
                pass
                #if args.config == ".":
                #    args.config = args.file
                #files.append(Path(args.config).expanduser())

        if filepath:
            fp = Path(filepath).expanduser()
            if fp.exists() and not fp.is_dir():
                if "# .coldtype" in fp.read_text():
                    files.append(fp)
        
        if args and args.file and args.config != "0":
            fp = Path(args.file).expanduser()
            if fp.exists() and not fp.is_dir():
                if "# .coldtype" in fp.read_text():
                    files.append(fp)

        py_config = {}
        for p in files:
            if p.exists() and p.suffix == ".py":
                try:
                    py_config = run_path(str(p), init_globals={
                        "__FILE__": p,
                        "__inputs__": self.inputs,
                        "__memory__": {},
                        "__as_config__": True,
                        "__sibling__": partial(sibling, p),
                    })
                    
                    self.config = ColdtypeConfig(py_config, self.config if self.config else None, args)

                    for f in self.config.font_dirs:
                        if f not in ALL_FONT_DIRS:
                            ALL_FONT_DIRS.insert(0, f)
                except Exception as e:
                    if isinstance(e, ColdtypeCeaseConfigException):
                        pass
                    else:
                        print("Failed to load config", p)
                        print("Exception:", e)
                        pass
        
        if len(files) == 0 or not self.config:
            self.config = ColdtypeConfig({}, None, args)
        
        self.config.args = args
        #print(self.config.values())
    
    def find_sources(self, dirpath, recursive=False):
        prefix = "**/" if recursive else ""
        globber = f"{prefix}*.py"
        if self.filepath:
            globber = f"{prefix}*" + self.filepath.suffix
        sources = list(dirpath.glob(globber))
        #sources.extend(list(dirpath.glob("*.md")))

        valid_sources = []
        for p in sources:
            if not p.name.startswith("_"):
                valid_sources.append(p)
            valid_sources = sorted(valid_sources, key=lambda p: str(p.relative_to(dirpath)))
            valid_sources = sorted(valid_sources, key=lambda p: str(p.relative_to(dirpath)).count("/") > 0)

        #for p in valid_sources:
        #    print(p.relative_to(dirpath))

        return valid_sources
    
    def blender_io(self):
        #if not self.use_blender and not self.config.blender_watch:
        #    return None

        bf = self.config.blender_file
        if not bf:
            bf = self.filepath.parent / "blends" / (self.filepath.stem + ".blend")
        return BlenderIO(bf)
    
    def normalize_filepath(self, filepath:Path, dirindex=0):
        if isinstance(filepath, str):
            filepath = Path(filepath)
        
        filepath = filepath.expanduser().resolve()

        if filepath.is_dir():
            self.dirpath = filepath
            #filepath = sorted(list(filepath.glob("*.py")), key=lambda p: p.stem)[dirindex]
            filepath = self.find_sources(self.dirpath)[dirindex]
        else:
            if self.dirpath is None:
                self.dirpath = filepath.parent

        if not filepath.exists():
            with_py = (filepath.parent / (filepath.stem + ".py"))
            if with_py.exists():
                filepath = with_py
        if filepath.suffix not in [".md", ".rst", ".py"]:
            raise Exception("Coldtype can only read .py, .md, and .rst files")
        
        return filepath
    
    def adjacents(self):
        if self.dirpath:
            return self.find_sources(self.dirpath)
    
    def reset_filepath(self, filepath:Path, code:str=None, reload:bool=True, dirdirection=0):
        self.unlink()
        self.should_unlink = False

        dirindex = 0
        if self.dirpath and dirdirection != 0:
            # find index of existing filepath, increment by dirdirection?
            pys = self.find_sources(self.dirpath)
            #pys = sorted(list(self.dirpath.glob("*.py")), key=lambda p: p.stem)
            curr = pys.index(self.filepath)
            adj = (curr + dirdirection) % len(pys)
            #print(curr, adj)
            filepath = pys[adj]
        
        if filepath:
            self.filepath = self.normalize_filepath(filepath, dirindex)
            if not self.filepath.exists():
                raise Exception("Source file does not exist")
        else:
            if code:
                self.write_code_to_tmpfile(code)
            else:
                raise Exception("Must provide filepath or code")
            
        if reload:
            self.reload()
        
        return self.filepath
    
    def reload(self,
        code:str=None,
        output_folder_override=None
        ):
        if code:
            self.write_code_to_tmpfile(code)
        
        self.codepath, self.data_out = read_source_to_tempfile(self.filepath, self.codepath, renderer=self.renderer)
        
        memory = {}
        if self.renderer:
            memory = self.renderer.state.memory
        
        source_code = self.codepath.read_text()
        version = None

        if re.findall(r"VERSIONS\s?=", source_code):
            versions = re.findall(r"VERSIONS\s?=.*\#\/VERSIONS", source_code, re.DOTALL)[0]
            versions = eval(re.sub("VERSIONS\s?=", "", versions))
            if not isinstance(versions, dict):
                versions = {str(idx):v for idx, v in enumerate(versions)}
            versions = {k:{**v, **dict(key=k)} for k,v in versions.items()}
            versions = list(versions.values())
            vi = self.renderer.source_reader.config.version_index
            version = versions[vi]
            self.renderer.state.versions = versions

            source_code = source_code.replace("ƒVERSION", version["key"])
            self.codepath.write_text(source_code)


        self.program = run_source(
            self.filepath,
            self.codepath,
            self.inputs,
            memory,
            __RUNNER__=self.runner,
            __BLENDER__=self.blender_io(),
            __VERSION__=version)
        
        self.candidates = self.renderable_candidates(
            output_folder_override, self.config.add_time_viewers)
    
    def write_code_to_tmpfile(self, code):
        if self.filepath:
            self.filepath.unlink()

        with NamedTemporaryFile("w", prefix="coldtype_", suffix=".py", delete=False) as tf:
            tf.write(code)
        
        self.filepath = Path(tf.name)
        self.should_unlink = True
    
    def renderable_candidates(self,
        output_folder_override=None,
        add_time_viewers=False,
        ):
        candidates = find_renderables(
            self.filepath,
            self.codepath,
            self.program,
            output_folder_override,
            blender_io=self.blender_io(),
            args=self.renderer.args if self.renderer else None)
        
        if len(candidates) == 0:
            candidates.append(Programs.Blank())
        
        if add_time_viewers:
            out = []
            for c in candidates:
                if (isinstance(c, animation) and
                    not isinstance(c, aframe) and
                    not isinstance(c, ui)
                    ):
                    out.extend(timeViewer(c))
                out.append(c)
            return out
        else:
            return candidates
    
    def renderables(self,
        viewer_solos=[],
        function_filters=[],
        class_filters=[],
        previewing=False,
        ):
        if not function_filters and self.config.function_filters:
            function_filters = self.config.function_filters
        
        return filter_renderables(self.candidates,
            viewer_solos=viewer_solos,
            function_filters=function_filters,
            class_filters=class_filters,
            previewing=previewing)
    
    def frame_results(self, frame, class_filters=[], renderer_state=None):
        rs = self.renderables(class_filters=class_filters)
        res = []
        for r in rs:
            if isinstance(r, runnable):
                res.append([r, None])
                continue
            
            ps = r.passes(None, renderer_state, indices=[frame])
            for p in ps:
                res.append([r, r.run_normal(p, renderer_state=renderer_state)])
        return res
    
    def unlink(self):
        if self.should_unlink and self.filepath:
            if self.filepath.exists():
                self.filepath.unlink()
        if self.codepath:
            if self.codepath.exists():
                self.codepath.unlink()
        return self


class Programs():
    @staticmethod
    def Demo():
        return SourceReader.LoadDemo("demo")[0]
    
    @staticmethod
    def Blank():
        return SourceReader.LoadDemo("blank")[0]
    
    @staticmethod
    def Glyphs(
        font=None,
        fontSize=54,
        showChars=False,
        rect=(1080, 1080)
        ):
        return SourceReader.LoadDemo("glyphs", **locals())[0]

    @staticmethod
    def Midi(
        file=None,
        duration=None,
        bpm=None,
        lookup=None,
        text=True,
        fps=30,
        rect=(1080, 540),
        log=False,
        preview_only=True,
        ):
        return SourceReader.LoadDemo("midi", **locals())[0]
    
    @staticmethod
    def VF(
        font=None,
        text="A",
        font_size=None,
        positions=(0, 1),
        stroke=False,
        seed=0,
        shuffle=False,
        animate=False,
        rect=(1080, 1080),
        log=False,
        preview_only=True,
        ):
        return SourceReader.LoadDemo("vf", **locals())[0]