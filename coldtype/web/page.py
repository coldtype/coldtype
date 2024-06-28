import re, frontmatter, markdown

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup

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
            raise Exception("Image not found", src_path)
        img = SkiaImage(src_path)
        width = img.width()
        mtime = int(src_path.stat().st_mtime)
        tq = "?t=" + str(mtime)
        img_tag['src'] = src + tq
        hires_version = src_path.parent / "hires" / src_path.name
        if hires_version.exists():
            a_tag["href"] = "/" + str(hires_version) + tq
        else:
            a_tag['href'] = img_tag['src']
        a_tag["target"] = "_blank"
        a_tag['style'] = f"max-width:{int(width/2)}px"
        img_tag['style'] = f"max-width:{int(width/2)}px"
        img_tag.wrap(a_tag)
    
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
    raw = markdown.markdown(text, extensions=["smarty", "mdx_linkify", "markdown_captions", "footnotes"])
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
    
    @staticmethod
    def load(file:Path, root:Path) -> "Page":
        data = frontmatter.loads(file.read_text())
        
        slug = data.get("slug", file.stem)
        title = data.get("title", "Untitled")
        template = data.get("template")
        if template is None:
            template = "_" + str(file.parent.stem)[:-1]
            print("TEMPLATE", template)

        preview_txt = data.content.split("+++")[0].replace("ßßß", "")
        preview_txt = re.sub(r'\[\^(\d+)\]', '', preview_txt)
        preview_image, preview = md_process(preview_txt, f"/{slug}", root)

        _, content = md_process(data.content
            .replace("+++", "<h5 class='continuation' id='continue-reading'>•••</h5>")
            .replace("ßßß", "<div class='spacer'></div>")
            .replace("---", "<div class='section'>•••</div>"), None, root)

        return Page(file, data.get("date"), slug, title, template, preview, content, data, preview_image)