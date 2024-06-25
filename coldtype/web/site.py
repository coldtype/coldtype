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

def render(metadata, pages, links, font_families):
    watch.append(root / "parts/header.j2")
    watch.append(root / "parts/footer.j2")

    footer = site_parts_env.get_template("footer.j2").render(standard_data)

    def render_page(template, title):
        template_path = root / "pages" / template
        watch.append(template_path)

        if title == None or title == "Home":
            header_title = metadata.get("title")
            path = sitedir / "index.html"
        else:
            header_title = metadata.get("title") + " | " + title
            path = sitedir / f"{template_path.stem}/index.html"

        page_links = []
        for k, v in links.items():
            current = k == title
            
            if isinstance(v, str):
                classes = []
            else:
                v, classes = v
            
            if current: classes.append("current")
            
            page_links.append(dict(title=k
                , current=current
                , href=v
                , external=v.startswith("http")
                , classes=" ".join(classes)))

        header = (site_parts_env.get_template("header.j2")
            .render({**standard_data, **dict(page_links=page_links)}))

        page_template = site_env.get_template(template)
        content = page_template.render(standard_data)
        
        path.parent.mkdir(exist_ok=True)

        path.write_text(generic_templates["page"].render({
            **standard_data, **dict(
                font_families=font_families
                , fonts=fonts
                , content=content
                , header=header
                , footer=footer
                , title=header_title
                , description=metadata["description"])}))
    
    for template, title in pages.items():
        render_page(template, title)

def todo():
    watch = []
    assetsdir = root / "assets"

    if assetsdir.exists():
        style = assetsdir / "style.css"
        if style.exists():
            watch.append(style)
        
        shutil.copytree(root / "assets", sitedir / "assets", dirs_exist_ok=True)

    def copy_to_multiserve():
        dst = multisitedir / root.stem
        shutil.copytree(sitedir, dst, dirs_exist_ok=True)

        for page in dst.glob("**/*.html"):
            html = Path(page).read_text()
            html = re.sub(r"=\"/", f'="/{root.stem}/', html)
            html = re.sub(r"url\('/", f"url('/{root.stem}/", html)
            Path(page).write_text(html)


#r = Rect(540/4, 540/4)

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
            print("HELLO WORLD")
            print(" ".join(["livereload", "-p", str(self.port), str(self.sitedir), "&>/dev/null", "&"]))
            os.system(" ".join(["livereload", "-p", str(self.port), str(self.sitedir), "&>/dev/null", "&"]))

        if self.multiport:
            if not is_port_in_use(multiport):
                os.system(" ".join(["livereload", "-p", str(multiport), str(self.multisitedir), "&>/dev/null", "&"]))

        standard_data = dict(
            version=version
            , year=year
            , root=self.root
            , sitedir=self.sitedir)
        
        page_links = []
        
        try:
            header = (self.site_env.get_template("_header.j2")
                .render({**standard_data, **dict(page_links=page_links)}))
            watch.append(self.root / "templates/_header.j2")
        except Exception as _:
            header = False
            print("no _header.j2 found")
        
        try:
            footer = (self.site_env.get_template("_footer.j2")
                .render({**standard_data, **dict(page_links=page_links)}))
            watch.append(self.root / "templates/_footer.j2")
        except Exception as _:
            footer = False
            print("no _footer.j2 found")

        print(standard_data)

        (self.sitedir / "index.html").write_text(generic_templates["page"].render({
            **standard_data, **dict(info=self.info
                , content="hello world"
                , header=header
                , footer=footer
                #, title=header_title
                #, description=metadata["description"]
                )
                }))

        super().__init__(rect, watch=watch, **kwargs)
    
    def kill(self):
        for _ in range(3):
            kill_process_on_port_unix(self.port)
            if self.multiport:
                kill_process_on_port_unix(self.multiport)


def exit(_):
    print("EXITING")
    return

    for _ in range(3):
        kill_process_on_port_unix(port)
        kill_process_on_port_unix(multiport)