"""Concatenate docsite/ pages (mkdocs nav order) into one markdown file for Opus.

Images become [image: alt]. Usage: python scripts/edop/dashboard/make_docs_markdown.py [out_path]
"""
import re, sys, yaml
from pathlib import Path
root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "docs/design/dashboard/edops_docs_for_opus.md"
class L(yaml.SafeLoader): pass
L.add_multi_constructor('tag:yaml.org,2002:python/', lambda l, s, n: None)
L.add_multi_constructor('!', lambda l, s, n: None)
nav = yaml.load((root/'mkdocs.yml').read_text(), Loader=L)['nav']
def walk(items, trail):
    for it in items:
        for title, v in it.items():
            if isinstance(v, list): yield from walk(v, trail+[title])
            else: yield trail+[title], v
img = re.compile(r'!\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?')
parts = ["# EDOPS documentation (docsite/), concatenated\n",
         "Generated from `docsite/` in nav order. Images replaced by `[image: alt text]`. Internal links are left as written.\n",
         "## Pages\n"]
pages = list(walk(nav, []))
for t, f in pages: parts.append(f"- {' > '.join(t)} (`{f}`)")
parts.append("")
n_img = 0
for t, f in pages:
    txt = (root/'docsite'/f).read_text()
    txt, k = img.subn(lambda m: f"[image: {m.group(1) or 'no alt text'}]", txt); n_img += k
    parts.append(f"\n\n---\n\n<!-- PAGE: {' > '.join(t)} | docsite/{f} -->\n\n{txt.strip()}\n")
out.write_text("\n".join(parts))
print(len(pages), "pages;", n_img, "images replaced;", out.stat().st_size, "bytes")
