from coldtype import *
import json, dateparser, markdown, jinja2

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from lxml.html import fragment_fromstring, tostring

from time import time
from datetime import datetime
from email.utils import format_datetime
from shutil import copytree

from coldtype.runon import Runon

class NotebookParser():
    def __init__(self
        , notebook_dir:Path
        , build_dir:Path
        , templates_dir:Path
        , assets_dir:Path
        , do_nest:bool = False
        , sort:dict = {}
        ) -> None:
        self.notebook_dir = notebook_dir
        self.build_dir = build_dir
        self.templates_dir = templates_dir
        self.assets_dir = assets_dir

        self.build_dir.mkdir(exist_ok=True)

        # TODO recursive glob to get a tree, to make a table-of-contents instead of only flat-list
        self.notebooks = list(self.notebook_dir.glob("**/*.ipynb"))
        print(">>>", self.notebooks)

        self.template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.templates_dir)))

        self.index_template = self.template_env.get_template("index.j2")
        self.post_template = self.template_env.get_template("post.j2")

        try:
            self.feed_template = self.template_env.get_template("feed.j2")
        except:
            self.feed_template = None

        posts = []

        self.build_unix = int(time())
        self.build_time = format_datetime(datetime.utcfromtimestamp(int(time()))).strip()

        for notebook in self.notebooks:
            if notebook.stem.startswith("_"):
                continue

            path = notebook.relative_to(self.notebook_dir)
            data = json.loads(Path(notebook).read_text())

            frontmatter = eval("".join(data["cells"][0]["source"]))

            slug = frontmatter.get("slug", ".".join(str(path).split(".")[:-1]))
            date = dateparser.parse(frontmatter["date"])
            date_string = date.strftime("%B %d, %Y")

            cells = []
            for c in data["cells"][1:]:
                ct = c["cell_type"]
                if ct == "markdown":
                    cells.append(dict(text=markdown.markdown("".join(c["source"]), extensions=["smarty", "fenced_code"])))
                elif ct == "code":
                    src = "".join(c["source"])
                    if src.strip().startswith("#hide-publish") or src.strip().startswith("#hide-blog"):
                        continue
                
                    lines = []
                    for line in src.splitlines():
                        if not line.strip().endswith("#hide-publish") and not line.strip().endswith("#hide-blog"):
                            lines.append(line)
                    
                    src = "\n".join(lines)
                    
                    highlit = fragment_fromstring(
                        highlight(src, PythonLexer(),
                            HtmlFormatter(linenos=False)))
                    html = tostring(highlit, pretty_print=True, encoding="utf-8").decode("utf-8")
                    cell = dict(html=html)

                    outputs = []
                    if "outputs" in c:
                        for o in c["outputs"]:
                            if o["output_type"] == "display_data" and o["data"] and "text/html" in o["data"]:
                                outputs.append(o["data"]["text/html"])
                                #print(o["data"]["text/html"][:10])
                            elif o.get("name") == "stdout":
                                outputs.append(["<pre class='stdout'>" + "".join(o["text"]) + "</pre>"])
                                #print(outputs[-1][10])
                            else:
                                pass
                    
                    if len(outputs) > 0:
                        cell["outputs"] = outputs
                    else:
                        cell["no-outputs"] = True
                    cells.append(cell)
            
            # need to be nested somehow

            post = dict(
                metadata={
                    **frontmatter,
                    "slug": slug,
                    **dict(
                        path=notebook,
                        pubDate=format_datetime(date).strip(),
                        date_string=date_string,
                        date=date)},
                notebook=notebook.stem,
                cells=cells)
            
            dst = self.build_dir / f"{slug}.html"
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            dst.write_text(self.post_template.render(dict(post=post, build_unix=self.build_unix)))

            posts.append(post)

        posts = list(reversed(sorted(posts, key=lambda p: p["metadata"]["date"])))

        if do_nest:
            class Post(Runon):
                def __init__(self, val):
                    super().__init__(None)
                    self._val = val
                
            nested_posts = Runon()

            for p in posts:
                slug = p["metadata"]["slug"]
                slugs = slug.split("/")[:-1]
                nested = nested_posts
                for s in slugs:
                    n = nested.find_(s, none_ok=True)
                    if not n:
                        n = Runon().tag(s)
                        nested.append(n)
                    nested = n
                nested.append(Post(p).tag(slug).data(post=True))
            
            def sorter(el, pos, data):
                if pos != 0:
                    sorter = sort[el.tag()]
                    def sortfn(x):
                        return sorter.index(x.tag().split("/")[-1])
                    el._els = list(sorted(el._els, key=sortfn))
            
            nested_posts.prewalk(sorter)
            posts = nested_posts

        copytree(self.assets_dir, self.build_dir / "assets", dirs_exist_ok=True)
        (self.build_dir / "index.html").write_text(self.index_template.render(dict(posts=posts, build_unix=self.build_unix)))
        
        if self.feed_template:
            (self.build_dir / "feed.xml").write_text(self.feed_template.render(dict(posts=posts, build=self.build_time, build_unix=self.build_unix)))
