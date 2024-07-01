import jinja2, os, re, subprocess

from coldtype.renderable import renderable
from coldtype.geometry import Rect
from coldtype.text import Style

from coldtype.web.server import maybe_run_server, kill_process_on_port_unix
from coldtype.web.fonts import woff2s
from coldtype.web.page import Page

from pathlib import Path
from random import randint
from datetime import datetime, timezone

generics_folder = Path(__file__).parent / "templates"
generics_env = jinja2.Environment(loader=jinja2.FileSystemLoader(generics_folder))
string_env = jinja2.Environment(loader=jinja2.BaseLoader())

try:
    from sourcetypes import jinja_html, css, js
except ImportError:
    jinja_html = str


nav_template: jinja_html = """
<nav>
    <ul>{% for n in nav_links %}
        <li><a href="{{n.href}}" {% if n.classes %}class="{{ n.classes }}" {% endif %}>{{n.title}}</a></li>
    {% endfor %}</ul>
</nav>
"""

class site(renderable):
    def __init__(self, root
        , port=8008
        , multiport=None
        , livereload=True
        , info=dict()
        , sources=None
        , generators=None
        , fonts=None
        , rect=Rect(200, 200)
        , watch=None
        , template=None
        , slugs="flat"
        , **kwargs
        ):
        self._watch = watch or []

        self._watch.append(generics_folder / "page.j2")
        
        self.root = root
        self.info = info
        self.livereload = livereload
        self.sources = sources or {}
        self.generators = generators or {}
        self.template_fn = template
        self.slugs = slugs
        
        self.port = port
        self.multiport = multiport

        self.generic_templates = {
            "page": generics_env.get_template("page.j2"),
            "notebook": generics_env.get_template("notebook.j2")
        }

        self.site_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.root / "templates")))

        self.sitedir = self.root / Path("_site")
        self.sitedir.mkdir(exist_ok=True)

        if self.multiport:
            self.multisitedir = Path("_site")
            self.multisitedir.mkdir(exist_ok=True)
        
        if fonts:
            self.fonts = woff2s(self.sitedir / "assets/fonts", fonts)
        else:
            self.fonts = []
        
        version = randint(0, 100000000)
        year = int(datetime.now().year)
        
        assetsdir = self.root / "assets"

        if assetsdir.exists():
            style = assetsdir / "style.css"
            if style.exists():
                self._watch.append(style)
        
            print("rsync assets")
            os.system(f'rsync -r {assetsdir}/ {self.sitedir / "assets"}')
            print("/rsync assets")

            if style.exists():
                style2 = (self.sitedir / "assets/style.css")
                style2.write_text(self.mod_css(style2.read_text()))
    
        rendersdir = self.root / "renders"

        if rendersdir.exists():
            print("rsync renders")
            os.system(f'rsync -r {rendersdir}/ {self.sitedir / "renders"}')
            print("/rsync renders")
    
        self.templates = {}
        for j2 in (self.root / "templates").glob("*.j2"):
            self._watch.append(j2)
            self.templates[j2.stem] = self.site_env.get_template(j2.name)
        
        for k, v in self.info.get("templates", {}).items():
            self.templates[k] = string_env.from_string(v)
        
        self.pages = []
        
        for file in (self.root / "pages").glob("**/*.md"):
            self._watch.append(file)
            page = Page.load_markdown(file, self.root, self.template_fn, self.slugs)
            self.pages.append(page)
        
        for file in (self.root / "pages").glob("**/*.ipynb"):
            # TODO could check gitignore here?
            self._watch.append(file)
            page = Page.load_notebook(file, self.root, self.generic_templates["notebook"], self.template_fn, self.slugs)
            self.pages.append(page)

        super().__init__(rect, watch=self._watch, **kwargs)

        build_time_utc = datetime.now(timezone.utc)
        rfc_822_format = "%a, %d %b %Y %H:%M:%S %z"
        formatted_time = build_time_utc.strftime(rfc_822_format)

        self.standard_data = dict(
            version=version
            , build=formatted_time
            , info=self.info
            , year=year
            , root=self.root
            , sitedir=self.sitedir
            , fonts=self.fonts
            , str=str)
        
        for k, v in self.sources.items():
            self.standard_data[k] = v(self)

        for k, _ in self.templates.items():
            if not k.startswith("_"):
                self.render_page(k)
            
        for page in self.pages:
            self.render_page(page)
        
        for k, g in self.generators.items():
            g(self)

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
    
    def mod_css(self, css):
        def expander(m):
            fontvar = f"{m[1]}-font"
            font = [f for f in self.fonts if f.variable_name == fontvar][0]
            props = eval(f"dict({m[2]})")
            style = Style(font.fonts[0].font, **props)
            fvs = ", ".join([f'"{k}" {int(v)}' for k,v in style.variations.items()])
            return f'font-family: var(--{fontvar}), sans-serif;\n    font-variation-settings: {fvs}'
        
        def inline_import(m):
            path = Path(m[1])
            if path.exists():
                self._watch.append(path)
                return f"/* start:{path} */\n\n" + self.mod_css(path.read_text()) + f"\n\n/* end:{path} */"
        
        css = re.sub(r"--([a-z]+)-font:\s?fvs\(([^\)]+)\)", expander, css)
        css = re.sub(r"@import \"([^\"]+)\";", inline_import, css)

        return css

    def header_footer(self, nav_links, url):
        nav_html = string_env.from_string(nav_template).render(nav_links=nav_links)

        header = self.templates.get("_header", False)
        if header:
            header = header.render({**self.standard_data, **dict(nav_links=nav_links, nav_html=nav_html, url=url)})
        
        footer = self.templates.get("_footer", False)
        if footer:
            footer = footer.render({**self.standard_data, **dict(nav_links=nav_links, nav_html=nav_html, url=url)})
        
        return header, footer
    
    def render_page(self, page:Page=None, data=None):
        nav = self.info.get("navigation", {})
        header_title = self.info.get("title")

        if isinstance(page, str):
            template_name = page
            page = None
        else:
            template_name = page.template
        
        wrap = True

        if template_name == "index":
            path = self.sitedir / "index.html"
            url = "/"
        elif page is not None:
            if page.title:
                header_title = header_title + " | " + page.title
            
            path = page.output_path(self.sitedir)
            url = f"/{page.slug}"
        else:
            # TODO way to get a custom title on a bare template
            url = f"/{template_name}"
            if "." in template_name:
                wrap = False
                path = self.sitedir / f"{template_name}"
            else:
                path = self.sitedir / f"{template_name}/index.html"
                

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
        
        header, footer = self.header_footer(nav_links, url)
        
        content = self.templates[template_name].render({**self.standard_data, **dict(page=page, url=url), **(data or {})})
        
        path.parent.mkdir(exist_ok=True, parents=True)

        #print("URL", url)
        
        if wrap:
            path.write_text(self.generic_templates["page"].render({
                **self.standard_data, **dict(
                    content=content
                    , url=url
                    , info=self.info
                    , header=header
                    , footer=footer
                    , title=header_title)}))
        else:
            path.write_text(content)
        
    def initial(self):
        kill_process_on_port_unix(self.port)
        maybe_run_server(self.livereload, self.port, self.sitedir)
        if self.multiport:
            kill_process_on_port_unix(self.multiport)
            maybe_run_server(self.livereload, self.multiport, self.multisitedir)
    
    def exit(self):
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