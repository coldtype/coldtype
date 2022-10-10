from urllib import parse
import requests
from urllib.parse import urlparse
from pathlib import Path

notebooks = {
    # "tutorials/geometry": 
    #     "1ldEBGu6z5kJBamnpCA1D71fecpZyFbPs",
    # "tutorials/text":
    #     "1E-q_UdRFkxQRI7Lx6OxDfTw_WBD4cyuI",
    # "tutorials/animation":
    #     "1sxNSdggg7mZmkQgSXG2WB2LwwtHA1UiK",
    "tutorials/shapes":
        "1mJ1QpXBSvf7gtSxQmpP8PCG_huit5_Ri"
}

for k, url in notebooks.items():
    #prs = urlparse(url)
    fid = url #prs.path.split("/")[-1]
    resp = requests.get(f"https://docs.google.com/uc?export=download&id={fid}")
    p = Path(f"docs/notebooks/{k}.ipynb")
    p.parent.mkdir(exist_ok=1, parents=1)
    p.write_bytes(resp.content)