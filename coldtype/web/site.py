import jinja2, os, shutil, re, livereload

from coldtype.renderable import renderable
from coldtype.geometry import Rect
from coldtype.web.server import is_port_in_use, kill_process_on_port_unix

from pathlib import Path
from random import randint
from datetime import datetime

generics_folder = Path(__file__).parent / "templates"
generics_env = jinja2.Environment(loader=jinja2.FileSystemLoader(generics_folder))

generic_templates = {
    "page": generics_env.get_template("page.j2"),
}

class site(renderable):
    def __init__(self, root, port=8008, multiport=None, info=dict(), rect=Rect(200, 200), watch=None, **kwargs):
        watch = watch or []
        
        self.root = root
        self.info = info
        
        self.port = port
        self.multiport = multiport

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
        
        os.system(f'rsync -vr {assetsdir}/ {self.sitedir / "assets"}')

        standard_data = dict(
            version=version
            , year=year
            , root=self.root
            , sitedir=self.sitedir)

        for template, title in self.info.get("pages").items():
            self.render_page(template, title, watch, standard_data)

        super().__init__(rect, watch=watch, **kwargs)

        if self.multiport:
            dst = self.multisitedir / root.stem
            dst.mkdir(exist_ok=True, parents=True)
            #shutil.copytree(sitedir, dst, dirs_exist_ok=True)

            os.system(f'rsync -vr {self.sitedir}/ {dst}')

            for page in dst.glob("**/*.html"):
                html = Path(page).read_text()
                html = re.sub(r"=\"/", f'="/{root.stem}/', html)
                html = re.sub(r"url\('/", f"url('/{root.stem}/", html)
                Path(page).write_text(html)
    
    def header_footer(self, watch, nav_links, standard_data):
        try:
            header = (self.site_env.get_template("_header.j2")
                .render({**standard_data, **dict(nav_links=nav_links)}))
            watch.append(self.root / "templates/_header.j2")
        except Exception as _:
            header = False
            print("no _header.j2 found")
        
        try:
            footer = (self.site_env.get_template("_footer.j2")
                .render({**standard_data, **dict(nav_links=nav_links)}))
            watch.append(self.root / "templates/_footer.j2")
        except Exception as _:
            footer = False
            print("no _footer.j2 found")
        
        return header, footer
    
    def render_page(self, template, title, watch, standard_data):
        template_path = self.root / "templates" / template
        watch.append(template_path)

        nav = self.info.get("navigation")
        header_title = self.info.get("title")

        if title == None or title == "Home":
            path = self.sitedir / "index.html"
        else:
            header_title = header_title + " | " + title
            path = self.sitedir / f"{template_path.stem}/index.html"

        nav_links = []
        for k, v in nav.items():
            current = k == title
            
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
        
        header, footer = self.header_footer(watch, nav_links, standard_data)

        page_template = self.site_env.get_template(template)
        content = page_template.render(standard_data)
        
        path.parent.mkdir(exist_ok=True)

        path.write_text(generic_templates["page"].render({
            **standard_data, **dict(
                content=content
                , info=self.info
                , header=header
                , footer=footer
                , title=header_title)}))
    
    def exit(self):
        for _ in range(3):
            kill_process_on_port_unix(self.port)
            if self.multiport:
                kill_process_on_port_unix(self.multiport)