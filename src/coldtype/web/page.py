import re, frontmatter, markdown, json

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Template
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from lxml.html import fragment_fromstring, tostring

from coldtype.img.skiaimage import SkiaImage

def count_words_in_markdown(markdown):
    text = markdown
    text = re.sub(r'<!--(.*?)-->', '', text, flags=re.MULTILINE)
    text = text.replace('\t', '    ')
    text = re.sub(r'[ ]{2,}', '    ', text)
    text = re.sub(r'^\[[^]]*\][^(].*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^( {4,}[^-*]).*', '', text, flags=re.MULTILINE)
    text = re.sub(r'{#.*}', '', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text)
    text = re.sub(r'</?[^>]*>', '', text)
    text = re.sub(r'[#*`~\-–^=<>+|/:]', '', text)
    text = re.sub(r'\[[0-9]*\]', '', text)
    text = re.sub(r'[0-9#]*\.', '', text)
    return len(text.split())

def wrap_images_with_links(html_string, grab_image, root:Path):
    soup = BeautifulSoup(html_string, 'html.parser')

    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        a_tag = soup.new_tag('a')
        src = img_tag["src"]
        src_path = root / Path(src[1:])
        if not src_path.exists():
            print("Image not found", src_path)
            img_tag['style'] = f"width:200px;height:200px"
        else:
            img = SkiaImage(src_path)
            width = img.width()
            mtime = int(src_path.stat().st_mtime)
            tq = "?t=" + str(mtime)
            img_tag['src'] = src + tq
            hires_version = src_path.parent / "hires" / src_path.name
            hires_link = None
            if hires_version.exists():
                hires_link = "/" + str(hires_version.relative_to(root)) + tq
            
            a_tag['href'] = img_tag['src']
            a_tag["target"] = "_blank"
            a_tag['style'] = f"max-width:{int(width/2)}px"
            img_tag['style'] = f"max-width:{int(width/2)}px"
            figcaption = img_tag.find_parent('figure').find("figcaption")
            img_tag['alt'] = figcaption.get_text(strip=True)
            img_tag.wrap(a_tag)
            
            if hires_link:
                existing_text = figcaption.string
                new_link = soup.new_tag('a', href=hires_link)
                new_link.string = "Hi-Res"
                figcaption.clear()  # Clear existing content
                figcaption.append(existing_text or "")
                figcaption.append(' / ')
                figcaption.append(new_link)
    
    for p_tag in soup.find_all('p'):
        length = len(p_tag.get_text(strip=True))
        if length == 0:
            p_tag.extract()
    
    if grab_image is not None:
        try:
            first_figure = soup.find("figure")
            first_figure.extract()
            first_figure.find("a")["href"] = grab_image
            first_figure.find("a")["target"] = ""
            first_figure.find("figcaption").extract()
            return str(first_figure), str(soup)
        except AttributeError:
            pass
    
    return None, str(soup)

def md_process(text, grab_image, root:Path):
    #text = text.replace("?_", "?_&nbsp;")
    raw = markdown.markdown(text, extensions=["smarty", "markdown_captions", "footnotes"])
    #return None, raw
    return wrap_images_with_links(raw, grab_image, root)

@dataclass
class Page:
    path: Path
    date: str
    slug: str
    title: str
    template: str
    preview: str
    content: str
    data: dict
    preview_image: str

    def date_rfc_822(self):
        if "/" in str(self.date):
            input_date = datetime.strptime(str(self.date) + " 18:00:00 +0000", "%m/%d/%Y %H:%M:%S %z")
        else:
            input_date = datetime.strptime(str(self.date) + " 18:00:00 +0000", "%Y-%m-%d %H:%M:%S %z")
        return input_date.strftime("%a, %d %b %Y %H:%M:%S %z")

    def word_count(self):
        return str(count_words_in_markdown(self.data.content))
    
    def image_count(self):
        count = 0
        for line in self.data.content.split("\n"):
            if line.strip().startswith('!['):
                count += 1
        return str(count)
    
    def unpublished(self):
        return self.date is None
    
    def output_path(self, sitedir:Path):
        op = sitedir / self.slug
        if str(op).endswith(".html"):
            return op
        else:
            return op / "index.html"
    
    @staticmethod
    def get_slug(file:Path, root:Path, slugs:str):
        if "nested" in slugs:
            slug = str(Path(file).relative_to(root / "pages").with_suffix(""))
        else:
            slug = file.stem
        
        if "html" in slugs:
            return slug + ".html"
        return slug
    
    @staticmethod
    def load_notebook(file:Path, root:Path, template:Template, template_fn=None, slugs="flat") -> "Page":
        data = json.loads(file.read_text())
        frontmatter = eval("".join(data["cells"][0]["source"]))

        default_slug = Page.get_slug(file, root, slugs)
        slug = frontmatter.get("slug", default_slug)
        
        frontmatter["notebook"] = True

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
                    cell["no_outputs"] = True
                cells.append(cell)
        
        notebook_html = template.render(cells=cells)
        
        title = frontmatter.get("title", "Untitled")
        
        if template_fn:
            page_template = template_fn(data)
        else:
            page_template = data.get("template")
            if page_template is None:
                page_template = "_" + str(file.parent.stem)[:-1]
        
        return Page(file, frontmatter.get("date"), slug, title, page_template, None, notebook_html, frontmatter, None)
    

    @staticmethod
    def load_markdown(file:Path, root:Path, template_fn=None, slugs="flat") -> "Page":
        data = frontmatter.loads(file.read_text())

        default_slug = Page.get_slug(file, root, slugs)
        
        slug = data.get("slug", default_slug)
        title = data.get("title", "Untitled")

        if template_fn:
            template = template_fn(data)
        else:
            template = data.get("template")
            if template is None:
                template = "_" + str(file.parent.stem)[:-1]

        preview_txt = data.content.split("+++")[0].replace("ßßß", "")
        preview_txt = re.sub(r'\[\^(\d+)\]', '', preview_txt)
        preview_image, preview = md_process(preview_txt, f"/{slug}", root)

        _, content = md_process(data.content
            .replace("+++", "<h5 class='continuation' id='continue-reading'>•••</h5>")
            .replace("ßßß", "<div class='spacer'></div>")
            .replace("---", "<div class='section'>•••</div>"), None, root)
        
        return Page(file, data.get("date"), slug, title, template, preview, content, data, preview_image)