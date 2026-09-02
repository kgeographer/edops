"""
One-time extractor: per-subregion rationale text from the Lovejoy article ->
data/lovejoy/lovejoy_rationales.md (the curated master Karl reviews/edits).

Source: articles/Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf, the
region-by-region section (pp. 8-22, "North Africa / Northwest" ... "Kalahari",
ends at "Conclusion").

Method:
  - Subregion + broad-region names are set bold in the PDF (fontname suffix ".B").
    We read the bold runs per page to get the ordered anchor sequence and each
    anchor's page number, then locate the matching sentence in the page text and
    slice span-start -> next-anchor-start.
  - Broad-region lead-in text (heading -> first child) is captured once, as an
    appendix for review context; it is NOT a geojson feature.
  - Cleanup is mechanical only: de-ligature, strip flattened footnote markers,
    repair line-wrap hyphenation, drop running heads/feet and the Table 1 block,
    normalise whitespace. No rewriting.
  - Flags (SHORT/LONG/NO_BOUNDARY_LANGUAGE/SPAN_UNCERTAIN/CROSS_PAGE) set review
    priority; nothing is auto-fixed.

After Karl's review this file is the source of truth; this script is not re-run.
build_lovejoy_geojson.py parses lovejoy_rationales.md and folds rationale + page
into app/static/workbench/lovejoy_regions.geojson.
"""
import json
import re
import statistics
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[3]
PDF = ROOT / "articles" / "Lovejoy_etal_defining-regions-of-pre-colonial-africa.pdf"
LPF = ROOT / "data" / "lovejoy" / "whg_dataset_1155.lpf"
OUT_MD = ROOT / "data" / "lovejoy" / "lovejoy_rationales.md"

PDF_PAGES = range(8, 23)  # 1-indexed inclusive 8..22

NAME_FIX = {"hc_10": "North Coast"}  # published LPF title typo "North Coaast"

# Broad-region headings, in document order, as they read in the running text.
BROAD = [
    "North Africa", "Saharan Africa", "West Africa",
    "West Central Africa", "East Africa", "Southern Africa",
]
BROAD_DESPACED = {b.replace(" ", ""): b for b in BROAD}

# Subregion display name -> regex that matches its name where it opens its
# discussion in the body text (the bold token, spaced form, tolerant of the
# article's minor variants). Keyed by the corrected display name.
SUBREGION_PAT = {
    "Northwest":            r"Northwest\b",
    "North Coast":          r"North Coa?ast\b",
    "Nile Valley":          r"Nile [Vv]alley\b",
    "Canarias":             r"Canarias\b",
    "Western Sahara":       r"Western Sahara\b",
    "Central Sahara":       r"Central Sahara\b",
    "Central Savanna":      r"Central Savanna\b",
    "Western Savanna":      r"Western Savanna\b",
    "Rivers":               r"Rivers is an awkward",
    "Forests":              r"Forests\b",
    "Voltaic":              r"Voltaic\b",
    "Western Bight":        r"Western Bight\b",
    "Eastern Bight":        r"Eastern Bight\b",
    "Cabo Verde":           r"Cabo Verde\b",
    "Gulf Islands":         r"Gulf Islands\b",
    "West Central North":   r"West Central North\b",
    "West Central South":   r"West Central South\b",
    "Rainforest":           r"Rainforest\b",
    "Southern Savanna":     r"Southern Savanna\b",
    "St. Helena":           r"St\.? Helena\b",
    "Horn":                 r"Horn sub-region\b",
    "Northeast":            r"Northeast sub-region\b",
    "Eastern Interior":     r"Eastern Interior\b",
    "Eastern Savanna":      r"Eastern Savanna\b",
    "Great Lakes":          r"Great Lakes\b",
    "East Coast":           r"East Coast\b",
    "East Central":         r"East Central\b",
    "Madagascar":           r"Madagascar\b",
    "Comoros":              r"Comoros\b",
    "Mascarenes":           r"Mascarenes\b",
    "Southern Grasslands":  r"Southern Grasslands\b",
    "South Central":        r"South Central\b",
    "Southeast":            r"Southeast\b",
    "Kalahari":             r"Kalahari\b",
}

BOUNDARY_TERMS = re.compile(
    r"\b(border|borders|bordered|extends?|extending|stretch|stretches|from|to the "
    r"(north|south|east|west)|north of|south of|east of|west of|river|mountains?|"
    r"range|coast|coastal|includes?|including|incorporates?|encompass|anchored|"
    r"boundary|boundaries|delimit|as far as|watershed|basin|plateau|highlands?)\b",
    re.I,
)


# Body prose is set at 10pt. 9pt = footnote block + running header, 8pt = the
# Table 1 controlled-vocabulary page, 6pt = superscript footnote markers +
# figure captions. Keeping only ~10pt strips all of it in one pass.
BODY_LO, BODY_HI = 9.4, 10.6


def _body_only(page):
    return page.filter(
        lambda o: o["object_type"] != "char" or BODY_LO <= o["size"] <= BODY_HI
    )


def bold_runs(page):
    """Ordered list of bold body-text runs on a page (de-spaced), reading order.
    Restricted to body-size chars so figure-caption bold doesn't leak in."""
    runs, cur = [], ""
    chars = [c for c in page.chars if BODY_LO <= c.get("size", 0) <= BODY_HI]
    for c in sorted(chars, key=lambda c: (round(c["top"]), c["x0"])):
        if c.get("fontname", "").endswith(".B"):
            cur += c["text"]
        else:
            if cur.strip():
                runs.append(cur.strip())
            cur = ""
    if cur.strip():
        runs.append(cur.strip())
    return [r for r in runs if len(r) > 1]


def page_text(page):
    return re.sub(r"\s+", " ", _body_only(page).extract_text(x_tolerance=1.2) or "").strip()


LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}


def clean(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    # flattened footnote markers: "Tripoli.22 As" -> "Tripoli. As" ; "Zombo.51" -> "Zombo."
    s = re.sub(r"(?<=[A-Za-z\"'])\.\d{1,3}(?=(\s|$|\"|'))", ".", s)
    # stray superscript number glued after a word, no period: "traffic29 Western"
    s = re.sub(r"(?<=[a-z])\d{1,3}(?=\s+[A-Z])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Sentences that enumerate a region's peoples. Capture the list tail up to the
# next sentence/clause boundary.
ETHN_TRIGGER = re.compile(
    r"(?:(?:major|key|principal|other|main|Malagasy)\s+)?"
    r"(?:ethnonyms|ethnolinguistic groups?|ethnic groups?|sub-?groups|inhabitants|"
    r"ethnolinguistic identities)\s+(?:[a-z’']+\s+){0,4}?"
    r"(?:included|include|consisted of|were|are|comprised|of)\s*:?\s*(.+?)(?:[.;])"
    r"|\b(?:classified as|designated|identified as|referred to as|"
    r"collectively (?:labeled|called|known as)|known locally as)\s+(.+?)(?:[.;])",
    re.I,
)
# tokens that are qualifiers, not names
ETHN_STOP = re.compile(
    r"\b(among|others?|other|more|broadly|particular|especially|general|generally|"
    r"most|many|slave|traders?|whom|were|not|the|in|of|as|and|or|that|is|are|"
    r"Cuba|Americas|Brazil|Atlantic|Africa)\b", re.I,
)


def extract_ethnonyms(text):
    """Best-effort comma list of peoples named in the span. Karl curates."""
    out, seen = [], set()
    for m in ETHN_TRIGGER.finditer(text):
        frag = m.group(1) or m.group(2) or ""
        # cut trailing qualifier clauses
        frag = re.split(r",?\s+(?:among\b|and others\b|but\b|although\b|who\b|"
                        r"which\b|especially\b|such as\b)", frag, maxsplit=1)[0]
        for part in re.split(r",|\band\b|\bor\b", frag):
            name = part.strip(" .,;:“”\"'")
            # drop a trailing subordinate clause ("Shona after c.1800" -> "Shona")
            name = re.split(r"\s+(?:after|before|who|which|from|in|of|as|by|during|"
                            r"more|sometimes|especially)\b", name)[0].strip()
            if not name or not name[0].isupper():
                continue
            if ETHN_STOP.search(name):
                continue
            if len(name) > 40 or name.count(" ") > 2:
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key)
                out.append(name)
    return out


def dehyphenate(s):
    """Repair line-wrap hyphenation ('north- ern' -> 'northern'). Returns
    (repaired, joins) where joins lists each collapsed token for review -- some
    will be genuine hyphens ('Essouk-Tadmekka') the rule wrongly fused."""
    joins = []

    def _j(m):
        tok = m.group(1) + m.group(2)
        joins.append(tok)
        return tok

    s = re.sub(r"(\w+)-\s+(\w+)", _j, s)
    return s, joins


def sentence_start(buf, pos):
    """Walk back from pos to the start of its sentence."""
    m = None
    for mm in re.finditer(r"(?:^|[.!?]\s+)(?=[A-Z(\"'])", buf[:pos + 1]):
        m = mm
    return m.end() if m else 0


def main():
    lpf = json.loads(LPF.read_text())
    feats = lpf["features"]
    # display name -> (src_id, macro)
    meta = {}
    order = []
    for f in feats:
        p = f["properties"]
        sid = p["src_id"]
        name = NAME_FIX.get(sid, p["title"])
        macro = (p.get("related") or [{}])[0].get("label", "")
        meta[name] = (sid, macro)
        order.append(name)

    # --- read pages: text buffer + offset->page, and ordered anchors ---
    buf = ""
    offsets = []              # (buf_pos, page_no)
    anchors_seq = []          # (kind, name, page_no)  in document order
    with pdfplumber.open(PDF) as pdf:
        for pn in PDF_PAGES:
            page = pdf.pages[pn - 1]
            txt = page_text(page)
            if txt:                       # skip the Table 1 page (no 10pt prose)
                offsets.append((len(buf), pn))
                buf += txt + "  "
            for run in bold_runs(page):
                for despaced, full in BROAD_DESPACED.items():
                    if despaced in run:
                        anchors_seq.append(("broad", full, pn))
                if run.rstrip(".") in ("Conclusion", "References"):
                    anchors_seq.append(("end", run.rstrip("."), pn))
                # subregion bold tokens are exact de-spaced names (+ maybe punctuation)
                tok = run.rstrip(",.")
                for name in order:
                    if tok == name.replace(" ", "").rstrip(",."):
                        anchors_seq.append(("sub", name, pn))

    def page_at(pos):
        pg = offsets[0][1]
        for off, p in offsets:
            if off <= pos:
                pg = p
        return pg

    # --- locate each anchor's char position in buf, in document order ---
    located = []   # (pos, kind, name, page_hint)
    cursor = 0
    seen = set()
    for kind, name, pn in anchors_seq:
        key = (kind, name)
        if key in seen:
            continue
        seen.add(key)
        if kind == "end":
            pat = re.escape(name)
        elif kind == "broad":
            # the heading occurrence, not an in-text mention ("... West Central
            # Africa. To maintain ...") -- headings are never followed by [.,]
            pat = re.escape(name) + r"(?![.,])"
        else:
            pat = SUBREGION_PAT[name]
        m = re.search(pat, buf[cursor:])
        if not m:
            # try from the top (anchor out of expected order)
            m2 = re.search(pat, buf)
            located.append((m2.start() if m2 else None, kind, name, pn))
            continue
        pos = cursor + m.start()
        located.append((pos, kind, name, pn))
        cursor = pos + 1

    # --- build spans ---
    pts = [(pos, kind, name, pn) for (pos, kind, name, pn) in located if pos is not None]
    pts.sort()
    records = {}      # name -> dict
    leadins = {}      # broad -> dict
    for i, (pos, kind, name, pn_hint) in enumerate(pts):
        if kind == "end":
            continue
        start = sentence_start(buf, pos)
        # end the span at the start of the next anchor's opening sentence, so the
        # next region's lead-in words don't dangle off this one
        end = sentence_start(buf, pts[i + 1][0]) if i + 1 < len(pts) else len(buf)
        raw = buf[start:end]
        if kind == "broad":                       # drop the glued heading token
            raw = re.sub(r"^" + re.escape(name) + r"\s+", "", raw)
        text, joins = dehyphenate(clean(raw))
        p_start = page_at(start)
        p_end = page_at(max(start, end - 1))
        page_str = str(p_start) if p_start == p_end else f"{p_start}–{p_end}"
        fns = sorted(set(int(x) for x in re.findall(r"(?<=[A-Za-z])\.(\d{1,3})\b", raw)))
        off_hint = pn_hint is not None and not (p_start - 1 <= pn_hint <= p_end + 1)
        rec = dict(text=text, page=page_str, p_start=p_start, p_end=p_end,
                   footnotes=fns, joins=joins, kind=kind, off_hint=off_hint,
                   ethnonyms=[] if kind == "broad" else extract_ethnonyms(text))
        if kind == "broad":
            leadins[name] = rec
        else:
            records[name] = rec

    # --- flags ---
    lengths = [len(r["text"]) for r in records.values() if r["text"]]
    med = statistics.median(lengths) if lengths else 0
    for name, rec in records.items():
        fl = []
        n = len(rec["text"])
        if med and n < med / 2:
            fl.append("SHORT")
        if med and n > med * 2:
            fl.append("LONG")
        if not BOUNDARY_TERMS.search(rec["text"]):
            fl.append("NO_BOUNDARY_LANGUAGE")
        if rec["p_start"] != rec["p_end"]:
            fl.append("CROSS_PAGE")
        if rec.get("off_hint"):
            fl.append("SPAN_UNCERTAIN")
        # only flag joins that fused a real hyphen (camelCase residue, e.g.
        # "EssoukTadmekka"); ordinary line-wrap joins are listed, not flagged
        if any(re.search(r"[a-z][A-Z]", j) for j in rec["joins"]):
            fl.append("HYPHEN_JOIN")
        rec["flags"] = fl
    for name in order:
        if name not in records:
            records[name] = dict(text="", page="", p_start=None, p_end=None,
                                 footnotes=[], joins=[], ethnonyms=[],
                                 flags=["SPAN_UNCERTAIN", "MISSING"])

    # --- emit markdown ---
    L = []
    L.append("# Lovejoy pre-colonial African subregions — article rationales")
    L.append("")
    L.append("Verbatim spans from *Defining Regions of Pre-Colonial Africa* "
             "(Lovejoy et al., **History in Africa** 48, 2021), pp. 8–22, extracted by "
             "`scripts/edop/workbench/build_lovejoy_rationale.py`. Mechanical cleanup only "
             "(de-ligature, footnote-marker strip, line-wrap hyphenation, whitespace); "
             "line-wrap repair sometimes fuses a real hyphen — those are listed per entry "
             "as `hyphen-joins`. `ethnonyms` is a best-effort list pulled from the span's "
             "\"Ethnonyms included …\" sentences — curate freely. **Review target:** the "
             "rationale paragraph, the `page` value, and `ethnonyms`. After review this file "
             "is the source of truth — `build_lovejoy_geojson.py` folds `text` + `page` + "
             "`ethnonyms` per `src_id` into the served geojson.")
    L.append("")
    L.append("<!-- PARSER CONTRACT (build_lovejoy_geojson.py):")
    L.append("     entry heading = '## <src_id> · <name>'          (keep verbatim)")
    L.append("     '- page:'      = string, e.g. 11  or  11–12 (en-dash)   — editable")
    L.append("     '- ethnonyms:' = comma-delimited list, may be empty     — editable")
    L.append("     body          = the paragraph(s) after the blank line below the last")
    L.append("                     '- ' line, up to the next '## ' — the rationale, verbatim")
    L.append("     '_missing_' body or MISSING flag => no rationale; needs hand-entry -->")
    L.append("")

    # summary table
    L.append("## Summary")
    L.append("")
    L.append("| src_id | subregion | macro | page | chars | ethn | flags |")
    L.append("|--------|-----------|-------|------|-------|------|-------|")
    for name in order:
        sid, macro = meta[name]
        r = records[name]
        L.append(f"| {sid} | {name} | {macro} | {r['page'] or '—'} | "
                 f"{len(r['text'])} | {len(r['ethnonyms'])} | {', '.join(r['flags']) or '—'} |")
    L.append("")
    L.append(f"_median span length: {int(med)} chars; "
             f"{sum(1 for n in order if not records[n]['text'])} missing_")
    L.append("")
    L.append("---")
    L.append("")

    # entries, macro-grouped in document order
    for name in order:
        sid, macro = meta[name]
        r = records[name]
        L.append(f"## {sid} · {name}")
        L.append("")
        L.append(f"- macro: {macro}")
        L.append(f"- page: {r['page']}")
        L.append(f"- flags: {', '.join(r['flags']) or 'none'}")
        L.append(f"- ethnonyms: {', '.join(r['ethnonyms'])}")
        if r["footnotes"]:
            L.append(f"- footnotes in span: {', '.join(map(str, r['footnotes']))}")
        if r["joins"]:
            L.append(f"- hyphen-joins (verify — some are real hyphens): {', '.join(r['joins'])}")
        L.append("")
        L.append(r["text"] if r["text"]
                 else "_missing — not captured by the extractor; enter by hand from the PDF._")
        L.append("")

    # broad-region lead-ins (review context; not geojson features)
    L.append("---")
    L.append("")
    L.append("## Appendix — broad-region lead-in text")
    L.append("")
    L.append("_Context between a broad-region heading and its first subregion. Not a map "
             "feature; here so the review can see boundary language that belongs to the "
             "first child region._")
    L.append("")
    for b in BROAD:
        r = leadins.get(b)
        L.append(f"### {b}")
        L.append("")
        if r and r["text"]:
            L.append(f"- page: {r['page']}")
            L.append("")
            L.append(r["text"])
        else:
            L.append("_none captured_")
        L.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L), encoding="utf-8")

    missing = [n for n in order if not records[n]["text"]]
    flagged = [n for n in order if records[n]["flags"] and n not in missing]
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    print(f"  {len(order)} subregions, {len(missing)} missing: {missing}")
    print(f"  flagged for review: {flagged}")
    print(f"  lead-ins captured: {sorted(leadins)}")


if __name__ == "__main__":
    main()
