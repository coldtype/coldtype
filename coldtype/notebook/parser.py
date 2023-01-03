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

class NotebookParser():
    def __init__(self
        , notebook_dir:Path
        , build_dir:Path
        , templates_dir:Path
        , assets_dir:Path
        ) -> None:
        self.notebook_dir = notebook_dir
        self.build_dir = build_dir
        self.templates_dir = templates_dir
        self.assets_dir = assets_dir

        self.build_dir.mkdir(exist_ok=True)
        self.notebooks = list(self.notebook_dir.glob("*.ipynb"))

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

            data = json.loads(Path(notebook).read_text())

            frontmatter = eval("".join(data["cells"][0]["source"]))

            slug = frontmatter["slug"]
            date = dateparser.parse(frontmatter["date"])
            date_string = date.strftime("%B %d, %Y")

            cells = []
            for c in data["cells"][1:]:
                ct = c["cell_type"]
                if ct == "markdown":
                    cells.append(dict(text=markdown.markdown("".join(c["source"]), extensions=["smarty", "mdx_linkify", "fenced_code"])))
                elif ct == "code":
                    src = "".join(c["source"])
                    if src.strip().startswith("#hide-publish"):
                        continue
                    
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
                    cells.append(cell)

            post = dict(
                metadata={
                    **frontmatter,
                    **dict(
                        path=notebook,
                        pubDate=format_datetime(date).strip(),
                        date_string=date_string,
                        date=date)},
                notebook=notebook.stem,
                cells=cells)
            
            (self.build_dir / f"{slug}.html").write_text(self.post_template.render(dict(post=post, build_unix=self.build_unix)))

            posts.append(post)

        posts = list(reversed(sorted(posts, key=lambda p: p["metadata"]["date"])))

        copytree(self.assets_dir, self.build_dir / "assets", dirs_exist_ok=True)
        (self.build_dir / "index.html").write_text(self.index_template.render(dict(posts=posts, build_unix=self.build_unix)))
        
        if self.feed_template:
            (self.build_dir / "feed.xml").write_text(self.feed_template.render(dict(posts=posts, build=self.build_time, build_unix=self.build_unix)))
