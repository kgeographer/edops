"""Split documentation/BasinATLAS_Catalog_v10.pdf into one single-page PDF per
attribute ID, using the master PDF's own outline (bookmarks) to resolve each ID's
page number -- no link-parsing or text heuristics needed. Output feeds the Codebook's
per-row deep links (generate_codebook.py) so BasinATLAS variables can point at their
provider's own page instead of being re-described by EDOPS.

Re-run only if documentation/BasinATLAS_Catalog_v10.pdf itself changes (it won't --
frozen external artifact). Output directory is gitignored, regenerable from the
already-tracked source PDF.

Usage: python3 scripts/edop/docsite/split_basinatlas_catalog.py
"""
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).parent.parent.parent.parent
SOURCE = ROOT / "documentation" / "BasinATLAS_Catalog_v10.pdf"
OUT_DIR = ROOT / "app" / "static" / "basinatlas_pages"

ATTRIBUTE_ID_RE = re.compile(r"^[A-Z]{1,2}\d{2}$")


def main():
    reader = PdfReader(SOURCE)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    for item in reader.outline:
        if isinstance(item, list):
            continue  # nested outline group, not a leaf bookmark
        title = item.title.strip()
        if not ATTRIBUTE_ID_RE.match(title):
            continue  # skip "Summary_Table" and any other non-attribute bookmarks

        page_num = reader.get_destination_page_number(item)
        writer = PdfWriter()
        # append(pages=(n, n+1)) rather than add_page(reader.pages[n]) -- add_page alone
        # left each output file carrying nearly the whole source document's shared
        # resources (~7.5MB per single page); append's page-range import correctly
        # limits the clone to what that one page actually references.
        writer.append(reader, pages=(page_num, page_num + 1))
        out_path = OUT_DIR / f"{title}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        written += 1

    print(f"Wrote {written} single-page PDFs to {OUT_DIR}")


if __name__ == "__main__":
    main()
