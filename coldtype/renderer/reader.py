import re, os
from pathlib import Path
from runpy import run_path
from functools import partial
from tempfile import NamedTemporaryFile

from coldtype.renderable import renderable
from coldtype.renderable.animation import animation

from coldtype.renderer.utils import Watchable
from coldtype.renderer.config import ColdtypeConfig
from coldtype.helpers import sibling
from coldtype.text.reader import ALL_FONT_DIRS

try:
    from docutils.core import publish_doctree
except ImportError:
    publish_doctree = None


def apply_syntax_mods(source_code, renderer=None):
    codepath_offset = 0

    def inline_arg(p):
        path = Path(inline.strip()).expanduser().absolute()
        if renderer:
            if path not in renderer.watchee_paths():
                renderer.watchees.append([Watchable.Source, path, None])
        src = path.read_text()
        codepath_offset = len(src.split("\n"))
        return src
    
    def inline_other(x):
        cwd = Path.cwd()
        path = Path(cwd / (x.group(1).replace(".", "/")+".py"))
        if renderer:
            if path not in renderer.watchee_paths():
                renderer.watchees.append([Watchable.Source, path, None])
        src = path.read_text()
        codepath_offset = len(src.split("\n"))
        return src

    if renderer and renderer.source_reader.config.inline_files:
        for inline in renderer.source_reader.config.inline_files:
            source_code = inline_arg(inline) + "\n" + source_code

    source_code = re.sub(r"from ([^\s]+) import \* \#INLINE", inline_other, source_code)
    source_code = re.sub(r"\-\.[A-Za-z_ƒ]+([A-Za-z_0-9]+)?\(", ".nerp(", source_code)
    source_code = re.sub(r"([\s]+)Ƨ\(", r"\1nerp(", source_code)
    #source_code = re.sub(r"λ[\s]{0,3}\.", "lambda p: p.", source_code)
    #source_code = re.sub(r"λ\s?([/\.\@]{1,2})", r"lambda xxx: xxx\1", source_code)
    #source_code = re.sub(r"λ\.", "lambda x: x.", source_code)
    #source_code = re.sub(r"λ", "lambda ", source_code)
    #source_code = re.sub(r"ßDPS\(([^\)]+)\)", r"(ß:=DPS(\1))", source_code)

    while "nerp(" in source_code:
        start = source_code.find("nerp(")
        end = -1
        i = 5
        depth = 1
        c = source_code[start+i]
        while depth > 0 and c:
            #print(c, depth)
            if c == "(":
                depth += 1
            elif c== ")":
                depth -= 1
            i += 1
            c = source_code[start+i]
        end = start+i
        source_code = source_code[:start] + "noop()" + source_code[end:]
        #print(start, end)
    
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
        for python in frag.findall("./pre/code[@class='python']"):
            blocks.append(python.text)
        source_code = "\n".join(blocks)
        if codepath and codepath.exists():
            codepath.unlink()
        with NamedTemporaryFile("w", prefix="coldtype_md_src", suffix=".py", delete=False) as tf:
            mod_src, _ = apply_syntax_mods(source_code, renderer)
            tf.write(mod_src)
            codepath = Path(tf.name)
    
    elif filepath.suffix == ".py":
        source_code, _ = apply_syntax_mods(filepath.read_text(), renderer)
        if codepath and codepath.exists():
            codepath.unlink()
        with NamedTemporaryFile("w", prefix=f"coldtype__{filepath.stem}_", suffix=".py", delete=False) as tf:
            tf.write(source_code)
            codepath = Path(tf.name)
    else:
        raise Exception("No code found in file!")
    
    return codepath, data_out


def run_source(filepath, codepath, **kwargs):
    return run_path(str(codepath), init_globals={
        "__COLDTYPE__": True,
        "__FILE__": filepath,
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
    viewer_solos=[],
    function_filters=[],
    class_filters=[],
    output_folder_override=None,
    ):
    all_rs = []
    filtered_rs = []
    
    for k, v in program.items():
        if isinstance(v, renderable) and not v.hidden:
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
        r.post_read()

    if any([r.solo for r in all_rs]):
        filtered_rs = [r for r in all_rs if r.solo]
    else:
        filtered_rs = all_rs
        
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
        cli_args=None,
        ):
        self.filepath = None
        self.codepath = None
        self.data_out = None
        self.dirpath = None
        self.should_unlink = False
        self.program = None
        self.renderer = renderer
        self.runner = runner

        self.config = None
        self.read_configs(cli_args, filepath)

        if filepath or code:
            self.reset_filepath(filepath, code)
    
    def read_configs(self, args, filepath):
        proj = Path(".coldtype.py")
        user = Path("~/.coldtype.py").expanduser()
        files = [user, proj]
        if args and hasattr(args, "config") and args.config:
            if args.config == "0":
                files = []
            else:
                if args.config == ".":
                    args.config = args.file
                files.append(Path(args.config).expanduser())

        if filepath:
            files.append(Path(filepath).expanduser())
        
        if args and args.file:
            fp = Path(args.file).expanduser()
            if fp.exists() and not fp.is_dir():
                files.append(fp)

        py_config = {}
        for p in files:
            if p.exists():
                try:
                    py_config = run_path(str(p), init_globals={
                        "__FILE__": p,
                        "__sibling__": partial(sibling, p),
                    })
                    #self.midi_mapping = py_config.get("MIDI", self.midi_mapping)
                    #self.hotkey_mapping = py_config.get("HOTKEYS", self.hotkey_mapping)
                    self.config = ColdtypeConfig(py_config, self.config if self.config else None, args)

                    for f in self.config.font_dirs:
                        ALL_FONT_DIRS.insert(0, f)
                except Exception as e:
                    print("Failed to load config", p)
                    print("Exception:", e)
        
        if len(files) == 0 or not self.config:
            self.config = ColdtypeConfig({}, None, args)
        
        self.config.args = args
        #print(self.config.values())
    
    def find_sources(self, dirpath):
        sources = list(dirpath.glob("*.py"))
        sources.extend(list(dirpath.glob("*.md")))

        valid_sources = []
        for p in sources:
            if not p.name.startswith("_"):
                valid_sources.append(p)
            valid_sources = sorted(valid_sources, key=lambda p: p.stem)
        
        return valid_sources
    
    def normalize_filepath(self, filepath:Path, dirindex=0):
        if isinstance(filepath, str):
            filepath = Path(filepath)
        
        filepath = filepath.expanduser().resolve()

        if filepath.is_dir():
            self.dirpath = filepath
            #filepath = sorted(list(filepath.glob("*.py")), key=lambda p: p.stem)[dirindex]
            filepath = self.find_sources(self.dirpath)[dirindex]
        else:
            self.dirpath = filepath.parent

        if not filepath.exists():
            with_py = (filepath.parent / (filepath.stem + ".py"))
            if with_py.exists():
                filepath = with_py
        if filepath.suffix not in [".md", ".rst", ".py"]:
            raise Exception("Coldtype can only read .py, .md, and .rst files")
        
        return filepath
    
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
            print(curr, adj)
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
    
    def reload(self, code:str=None):
        if code:
            self.write_code_to_tmpfile(code)
        
        self.codepath, self.data_out = read_source_to_tempfile(self.filepath, self.codepath, renderer=self.renderer)
        self.program = run_source(
            self.filepath,
            self.codepath,
            __RUNNER__=self.runner)
    
    def write_code_to_tmpfile(self, code):
        if self.filepath:
            self.filepath.unlink()

        with NamedTemporaryFile("w", prefix="coldtype_", suffix=".py", delete=False) as tf:
            tf.write(code)
        
        self.filepath = Path(tf.name)
        self.should_unlink = True
    
    def renderables(self,
        viewer_solos=[],
        function_filters=[],
        class_filters=[],
        output_folder_override=None,
        ):
        if not function_filters and self.config.function_filters:
            function_filters = self.config.function_filters
        return find_renderables(
            self.filepath,
            self.codepath,
            self.program,
            viewer_solos,
            function_filters,
            class_filters,
            output_folder_override)
    
    def frame_results(self, frame, class_filters=[]):
        rs = self.renderables(class_filters=class_filters)
        res = []
        for r in rs:
            ps = r.passes(None, None, indices=[frame])
            for p in ps:
                res.append([r, r.run_normal(p)])
        return res
    
    def unlink(self):
        if self.should_unlink and self.filepath:
            if self.filepath.exists():
                self.filepath.unlink()
        if self.codepath:
            if self.codepath.exists():
                self.codepath.unlink()
        return self