"""
Build app/static/workbench/lovejoy_region_notes.json for the African Regions tab.

Per-region rationale pulled from the Lovejoy article
(articles/Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf, pp. 12-23 --
the region-by-region description section), keyed by src_id:

    {src_id: {name, page, blurb, rationale, needs_review}}

  blurb        - the one-line description from the published WHG LPF (kept as short form)
  rationale    - the article's defining paragraph(s) for the region (fuller)
  needs_review - true where the automatic slice is short or didn't clearly start on
                 the region's defining sentence; hand-finish those against
                 data/lovejoy/lovejoy_regions_prose.txt (also written here).

Automatic extraction is a scaffold, not the final word -- ~27/34 land clean, the
rest are flagged. Re-runnable.
"""
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[3]
PDF = ROOT / "articles" / "Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf"
LPF = ROOT / "data" / "lovejoy" / "whg_dataset_1155.lpf"
OUT_JSON = ROOT / "app" / "static" / "workbench" / "lovejoy_region_notes.json"
OUT_PROSE = ROOT / "data" / "lovejoy" / "lovejoy_regions_prose.txt"

NAME_FIX = {"hc_10": "North Coast"}  # published title typo "North Coaast"

# Defining-sentence anchors -- the phrasing the article actually uses to open each
# region's paragraph. Keyed by the published dataset title.
DEF = {
    "North Coaast": r"\bNorth Coast (encompasses|refers|comprises|includes|is |extends)",
    "Nile Valley": r"\bNile [Vv]alley (encompasses|comprises|includes|refers|is |extends|covers|constitutes)",
    "Northwest": r"\bNorthwest\b[^.]{0,90}?\b(encompasses|refers|comprises|includes|extends|anchored|is )",
    "Rivers": r"\bRivers\b[^.]{0,90}?\b(refers|encompasses|comprises|is defined|extends|includes)|\bRivers of Guinea\b",
    "Canarias": r"\bCanarias are an archipelago\b",
    "Western Sahara": r"\bWestern Sahara borders the Atlantic\b",
    "Central Sahara": r"\bCentral Sahara includes\b",
    "Central Savanna": r"\bCentral Savanna is\b",
    "Western Savanna": r"\bWestern Savanna is anchored\b",
    "Forests": r"\bForests refers to\b",
    "Voltaic": r"\bVoltaic to describe the basin\b",
    "Western Bight": r"\bWestern Bight typically conflates\b",
    "Eastern Bight": r"\bEastern Bight refers to\b",
    "Cabo Verde": r"\bCabo Verde islands were uninhabited\b",
    "Gulf Islands": r"\bGulf Islands are part of a line of volcanoes\b",
    "West Central North": r"\bWest Central North incorporates\b",
    "West Central South": r"\bWest Central South includes\b",
    "Rainforest": r"\bThe equatorial Rainforest comprises\b",
    "Southern Savanna": r"\bSouthern Savanna extends\b",
    "St. Helena": r"\bSt\.? Helena, which is over 3,000\b",
    "Horn": r"\bthe Horn sub-region contains\b",
    "Northeast": r"\bThe Northeast sub-region encompasses\b",
    "Eastern Interior": r"\bEastern Interior includes\b",
    "Eastern Savanna": r"\bEastern Savanna incorporates\b",
    "Great Lakes": r"\bGreat Lakes form around\b",
    "East Coast": r"\bEast Coast, or Swahili coast\b",
    "East Central": r"\bEast Central lies between\b",
    "Madagascar": r"\bMadagascar was both a source\b",
    "Comoros": r"\bThe Comoros are located\b",
    "Mascarenes": r"\bThe Mascarenes are centered\b",
    "Southern Grasslands": r"\bSouthern Grasslands extends\b",
    "South Central": r"\bSouth Central is the Zimbabwe plateau\b",
    "Southeast": r"\bSoutheast\b[^.]{0,80}?\b(consists|comprises|includes|extends|relates|is )",
    "Kalahari": r"\bKalahari\b[^.]{0,120}?\b(desert|is |comprises|includes|extends|covers|had low)",
}


def main():
    lpf = json.loads(LPF.read_text())
    feats = lpf["features"]
    sid_of = {f["properties"]["title"]: f["properties"]["src_id"] for f in feats}
    blurb_of = {
        f["properties"]["src_id"]: ((f["properties"].get("descriptions") or [{}])[0].get("value", "") or "").strip()
        for f in feats
    }

    pagetext = {}
    with pdfplumber.open(PDF) as pdf:
        for i, pg in enumerate(pdf.pages):
            pn = i + 1
            if not (11 <= pn <= 23):
                continue
            t = pg.extract_text(x_tolerance=1.2) or ""
            keep = []
            for ln in t.split("\n"):
                s = ln.strip()
                if not s or s.startswith("https://doi.org"):
                    continue
                if re.fullmatch(r"(Defining Regions of Pre-Colonial Africa|History in Africa)\s*\d*", s):
                    continue
                if re.fullmatch(r"\d+\s+History in Africa", s):
                    continue
                if re.match(r"^\d{1,3}\s+[A-Z].{0,4}[a-z].*,\s", s) and len(s) > 45:
                    continue
                keep.append(s)
            pagetext[pn] = " ".join(keep)

    offsets, buf = [], ""
    for pn in sorted(pagetext):
        offsets.append((len(buf), pn))
        buf += pagetext[pn] + "  "

    def page_at(o):
        pg = offsets[0][1]
        for off, p in offsets:
            if off <= o:
                pg = p
        return pg

    found = []
    for nm, sid in sid_of.items():
        pat = DEF.get(nm)
        if not pat:
            continue
        m = re.search(pat, buf, re.I | re.S)
        if m:
            found.append((m.start(), nm, sid))
    found.sort()

    notes = {}
    for i, (pos, nm, sid) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else min(pos + 1500, len(buf))
        c = re.sub(r"\s+", " ", buf[pos:end]).strip()
        c = re.sub(r"\s+\d{1,3}\s+[A-Z][a-z]+ [A-Z][a-z].*$", "", c)
        c = re.sub(r"\s+(Making Identity|A History of|River of Wealth).*$", "", c)
        c = c[:1100].strip()
        notes[sid] = {"name": NAME_FIX.get(sid, nm), "page": page_at(pos),
                      "blurb": blurb_of[sid], "rationale": c}

    for nm, sid in sid_of.items():
        if sid not in notes:
            notes[sid] = {"name": NAME_FIX.get(sid, nm), "page": None,
                          "blurb": blurb_of[sid], "rationale": "", "needs_review": True}
        else:
            n = notes[sid]
            n["needs_review"] = len(n["rationale"]) < 220 or nm.lower() not in n["rationale"][:90].lower()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({k: notes[k] for k in sorted(notes)}, indent=1, ensure_ascii=False), encoding="utf-8")
    OUT_PROSE.write_text("\n\n".join(f"[p{p}]\n{pagetext[p]}" for p in sorted(pagetext)), encoding="utf-8")

    review = sorted(notes[s]["name"] for s in notes if notes[s]["needs_review"])
    print(f"wrote {OUT_JSON.relative_to(ROOT)}  ({34 - len(review)}/34 clean)")
    print(f"needs_review: {review}")
    print(f"wrote {OUT_PROSE.relative_to(ROOT)} (curation aid)")


if __name__ == "__main__":
    main()
