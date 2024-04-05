import requests
import urllib.parse
from pathlib import Path

urls = [
    "https://colab.research.google.com/drive/1oUwv9mxG-Q14-zTtY0lhhGmtuuRChaN-#scrollTo=NpQirv6FZLCm",
    "https://colab.research.google.com/drive/1_RHh5tw-Qc9ZMZHyImkcb-qh8yWdPNgk#scrollTo=Hj35zB-CgNP6",
    "https://colab.research.google.com/drive/1IQnOZuvmNYO5k-VopgwZwl41Rqa0kE8Y#scrollTo=2EO14TTlvXQO",
]

for url in urls:
    doc_id = urllib.parse.urlparse(url).path.split("/")[-1]
    download_url = f"https://docs.google.com/uc?export=download&id={doc_id}"
    res = requests.get(download_url)
    downloads = Path(__file__).parent / "downloads"
    downloads.mkdir(exist_ok=True, parents=True)
    (downloads / f"{doc_id}.ipynb").write_text(res.text)

    print(">", doc_id)