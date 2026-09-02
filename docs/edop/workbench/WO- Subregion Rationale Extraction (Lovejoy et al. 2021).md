# WO: Subregion Rationale Extraction (Lovejoy et al. 2021)

*Draft for CC — 31 August 2026*

## Goal

For each of the 34 subregions in Lovejoy et al., *Defining Regions of Pre-Colonial
Africa* (History in Africa 48, 2021), extract the verbatim article text that presents
that subregion's rationale, with page numbers, suitable for quoting in the African
Regions panel.

**Verbatim only.** No rewriting, no summarising, no interpretation. The output is
quotable source text with provenance. Karl reviews all 34 by hand; the goal is to
make that review fast, not to eliminate it.

## Source

The article PDF. Work from the text layer. Section structure is:

- Six broad-region headings (North Africa, Saharan Africa, West Africa, West Central
  Africa, East Africa, Southern Africa).
- Under each, subregion discussions introduced by the subregion name in bold at the
  start of a sentence (e.g. "The **Northwest** sub-region overlaps with...",
  "**Central Savanna** is landlocked and...").
- Subregion names match the controlled vocabulary in Table 1.

## Extraction rules

1. **Span start.** The sentence containing the first bold occurrence of the subregion
   name under its parent broad-region heading. Include the full sentence, not just
   from the bold token.
2. **Span end.** Immediately before the next subregion's span start, or the next
   broad-region heading, whichever comes first.
3. **Keep** everything in the span, including ethnonym lists and trade/polity
   narrative. Do not trim to "the environmental part" — the mix of claim types is the
   point.
4. **Broad-region lead-in.** Capture the text between a broad-region heading and its
   first subregion span **once**, stored on the parent. Do not duplicate it into each
   child. (This is the most likely source of disagreement between the earlier two
   passes — the West Africa lead-in runs over a page before reaching Central Savanna.)
5. **Page numbers.** Record start and end page for each span. If a span crosses pages,
   record both.
6. **Cleanup, mechanical only:**
   - Strip footnote reference markers (e.g. trailing `.51`, `.22`) — these are
     superscripts flattened into the text layer.
   - Repair line-break hyphenation (`north- ern` → `northern`). Preserve genuine
     hyphens.
   - Normalise whitespace and remove running headers/footers
     (`History in Africa`, `Defining Regions of Pre-Colonial Africa`,
     `https://doi.org/10.1017/hia.2020.17 Published online by Cambridge University Press`).
   - Preserve diacritics and non-Latin transliterations as they appear.
7. **Footnote text itself** is out of scope. Record the footnote numbers that occurred
   within the span if cheap, so citations can be chased later.

## Output

One record per subregion:

```
subregion_name
parent_broad_region
rationale_text        (verbatim, cleaned)
page_start, page_end
footnote_refs         (list, optional)
flags                 (list, see below)
```

Plus one record per broad region for the lead-in text.

Format: whatever slots into the existing panel data path most cleanly — JSON or TSV,
CC's call.

## Flagging for review

Do not fix anomalies. Flag them so Karl's pass has a priority order.

- `SHORT` / `LONG` — span length more than ~2x from the median span length.
- `NO_BOUNDARY_LANGUAGE` — span contains no spatial-extent terms (border, extends,
  from/to, north/south/east/west of, river, mountain, coast, includes).
- `SPAN_UNCERTAIN` — bold subregion name not found, or found more than once outside
  the expected position; span boundaries inferred rather than matched.
- `CROSS_PAGE` — span crosses a page break (higher risk of header/footer contamination).

Unflagged records should be reviewable at a glance.

## If / then: when to escalate beyond deterministic extraction

Default is deterministic. Escalate **only** for the residue.

**If** fewer than ~5 records carry `SPAN_UNCERTAIN` or `NO_BOUNDARY_LANGUAGE` →
**then** no model call. Karl fixes them by hand during review; 5 items is minutes.

**If** more than ~5 records are flagged uncertain, or the bold-name anchor proves
unreliable across the PDF text layer (formatting lost, bold not encoded) → **then**
one Opus call, scoped narrowly:

> Given this page range of article text and this list of subregion names, identify
> the character offsets at which each subregion's discussion begins and ends. Return
> offsets only. Do not return, rewrite, or summarise the text.

The model returns boundaries; CC does the slicing. This keeps the text verbatim by
construction — the model never touches the string that ends up in the panel.

**If** the PDF text layer is too degraded for either approach (columns interleaved,
OCR noise, ligatures broken beyond rule-based repair) → **then** stop and tell Karl
before spending more time. A cleaner source (publisher HTML, the Cambridge Core
version) is likely faster than fighting the extraction.

**Do not** call a model to clean, normalise, or improve the extracted prose. Cleanup
is rules or it is Karl.

**Fable** is not indicated for any step here — nothing in this task needs capability
beyond boundary-finding, and verbatim fidelity is better served by less model
involvement, not more.

## Done when

All 34 subregions have a verbatim span with page numbers, flags are assigned, and the
records load into the African Regions info panel. Karl's review pass follows.
