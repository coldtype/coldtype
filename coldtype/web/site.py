import jinja2, os, re, subprocess

try:
    import livereload
except ImportError:
    print("> pip install livereload")

from coldtype.renderable import renderable
from coldtype.geometry import Rect
from coldtype.web.server import is_port_in_use, kill_process_on_port_unix

from pathlib import Path
from random import randint
from datetime import datetime

generics_folder = Path(__file__).parent / "templates"

generics_env = jinja2.Environment(loader=jinja2.FileSystemLoader(generics_folder))

string_env = jinja2.Environment(loader=jinja2.BaseLoader())


try:
    from sourcetypes import jinja_html
except ImportError:
    jinja_html = str


nav_template: jinja_html = """
<ul>{% for n in nav_links %}
    <li><a href="{{n.href}}" {% if n.classes %}class="{{ n.classes }}" {% endif %}>{{n.title}}</a></li>
{% endfor %}</ul>
"""

class site(renderable):
    def stub(self, _path, content=None):
        path = self.root / _path
        if not path.exists():
            if content is None:
                path.mkdir(parents=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        return path
    
    def __init__(self, root, port=8008, multiport=None, info=dict(), rect=Rect(200, 200), watch=None, **kwargs):
        watch = watch or []

        watch.append(generics_folder / "page.j2")
        
        self.root = root
        self.info = info
        
        # self.stub("assets/style.css", "body { background: pink; }")
        # self.stub("assets/fonts")
        # self.stub("templates/_header.j2", "Header")
        # self.stub("templates/index.j2", "This is the index page")
        # self.stub("templates/_footer.j2", "Footer")
        
        self.port = port
        self.multiport = multiport

        self.generic_templates = {
            "page": generics_env.get_template("page.j2"),
        }

        self.site_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.root / "templates")))

        self.sitedir = self.root / Path("_site")
        self.sitedir.mkdir(exist_ok=True)

        if self.multiport:
            self.multisitedir = Path("_site")
            self.multisitedir.mkdir(exist_ok=True)
        
        version = randint(0, 100000000)
        year = int(datetime.now().year)

        if not is_port_in_use(self.port):
            os.system(" ".join(["livereload", "-p", str(self.port), str(self.sitedir), "&>/dev/null", "&"]))

        if self.multiport:
            if not is_port_in_use(multiport):
                os.system(" ".join(["livereload", "-p", str(multiport), str(self.multisitedir), "&>/dev/null", "&"]))
        
        assetsdir = self.root / "assets"

        if assetsdir.exists():
            style = assetsdir / "style.css"
            if style.exists():
                watch.append(style)
        
        os.system(f'rsync -r {assetsdir}/ {self.sitedir / "assets"}')

        standard_data = dict(
            version=version
            , info=self.info
            , year=year
            , root=self.root
            , sitedir=self.sitedir)
    
        templates = {}
        for j2 in (self.root / "templates").glob("*.j2"):
            watch.append(j2)
            templates[j2.stem] = self.site_env.get_template(j2.name)
        
        for k, v in self.info.get("templates", {}).items():
            templates[k] = string_env.from_string(v)
        
        self.templates = templates

        for k, _ in self.templates.items():
            self.render_page(k, None, standard_data)

        super().__init__(rect, watch=watch, **kwargs)

        if self.multiport:
            dst = self.multisitedir / root.stem
            dst.mkdir(exist_ok=True, parents=True)
            #shutil.copytree(sitedir, dst, dirs_exist_ok=True)

            os.system(f'rsync -r {self.sitedir}/ {dst}')

            for page in dst.glob("**/*.html"):
                html = Path(page).read_text()
                html = re.sub(r"=\"/", f'="/{root.stem}/', html)
                html = re.sub(r"url\('/", f"url('/{root.stem}/", html)
                Path(page).write_text(html)
    
    def header_footer(self, nav_links, standard_data):
        nav_html = string_env.from_string(nav_template).render(nav_links=nav_links)

        header = self.templates.get("_header", False)
        if header:
            header = header.render({**standard_data, **dict(nav_links=nav_links, nav_html=nav_html)})
        
        footer = self.templates.get("_footer", False)
        if footer:
            footer = footer.render({**standard_data, **dict(nav_links=nav_links, nav_html=nav_html)})
        
        return header, footer
    
    def render_page(self, template_name, title, standard_data):
        if template_name in ["_header", "_footer"]:
            return None
        
        nav = self.info.get("navigation", {})
        header_title = self.info.get("title")

        if template_name == "index":
            path = self.sitedir / "index.html"
            url = "/"
        else:
            if title:
                header_title = header_title + " | " + title
            path = self.sitedir / f"{template_name}/index.html"
            url = f"/{template_name}"

        nav_links = []
        for k, v in nav.items():
            current = v == url
            
            if isinstance(v, str):
                classes = []
            else:
                v, classes = v
            
            if current: classes.append("current")
            
            nav_links.append(dict(title=k
                , current=current
                , href=v
                , external=v.startswith("http")
                , classes=" ".join(classes)))
        
        header, footer = self.header_footer(nav_links, standard_data)
        
        content = self.templates[template_name].render(standard_data)
        
        path.parent.mkdir(exist_ok=True)

        path.write_text(self.generic_templates["page"].render({
            **standard_data, **dict(
                content=content
                , info=self.info
                , header=header
                , footer=footer
                , title=header_title)}))
    
    def exit(self):
        print("EXITING")
        from time import sleep
        for _ in range(1):
            kill_process_on_port_unix(self.port)
            if self.multiport:
                kill_process_on_port_unix(self.multiport)
    
    def upload(self, bucket, region="us-east-1", profile=None):
        args_nocache = [
            "aws", "s3",
            "--region", region,
            "sync",
            "--cache-control", "no-cache",
            "--exclude", "*",
            "--include", "*.html",
            "--include", "*.xml",
            self.sitedir,
            f"s3://{bucket}"
        ]
        
        args_cache = [
            "aws", "s3",
            "--region", region,
            "sync",
            self.sitedir,
            f"s3://{bucket}",
            "--exclude", ".git/*",
            "--exclude", "venv/*",
            "--exclude", "*.html"
        ]

        if profile is not None:
            args_nocache.extend(["--profile", profile])
            args_cache.extend(["--profile", profile])
        
        subprocess.run(args_nocache)
        subprocess.run(args_cache)

        print("/upload")