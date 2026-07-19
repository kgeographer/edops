# WO1 findings — CDOP pilot page + L08 lens similarity

**Branch:** `cdop_pilot` (cut from `cdop`)
**Page:** `http://localhost:8000/cdop`
**Date:** 2026-07-18

---

## Plumbing: success

All structural parts of WO1 are implemented and functional:

- `cdop_pilot.html` loads at `/cdop`; three tabs render (Societies active, Ecoregions, WH Cities)
- Dropped tabs (Main, Basins, WH Sites) are cleanly absent
- L08 index builds at startup (~4 s, ~17 MB; confirmed in notebook `wo_l08_similarity.ipynb`)
- `GET /api/whc-similar-env-lens` route responds correctly; lens dropdown populates;
  `filter_hybas_ids` corpus restriction works — results are from within the 254-city corpus
- Heading and description updated: "5 most similar cities in this collection (lens name)" +
  "corpus-relative ranking by climate-lens distance (L08 basin index)"
- 254/258 count shown in panel subhead
- Old `/workbench` route and page untouched

---

## Accept gate: partially met, partially failed

The WO accept gate was:

> Mombasa, under a climate lens, returns no Arid/Desert or Mediterranean/Dry Temperate
> neighbours in its top 5. If Jerusalem is still in the list, the WO has failed.

Results by lens:

### Temperature regime — PASS

Top 5: Trinidad (Cuba), Camagüey (Cuba), Santa Cruz de Mompox (Colombia), Galle (Sri Lanka),
Santa Ana de Coro (Venezuela).

All tropical, all low-latitude. No Arid/Desert, no Mediterranean, no Jerusalem. The
temperature lens discriminates Mombasa correctly. This is the instrument doing what it should.

### Seasonal phase — QUESTIONABLE FAIL

Top 5: George Town (Malaysia), **Split (Croatia)**, Salvador (Brazil), **Ibiza (Spain)**,
**Vatican City (Holy See)**.

George Town and Salvador are defensible tropical matches. But Split, Ibiza, and Vatican City
are Mediterranean climates. Three of five neighbours are climatologically wrong.

### Precipitation regime — CLEAR FAIL

Top 5: **Augsburg (Germany)**, Quito (Ecuador), **Salzburg (Austria)**, **Kotor (Montenegro)**,
**Tinn (Norway)**.

Four of five are temperate European or high-altitude cities with no climate resemblance to
Mombasa. This is the most striking failure.

---

## Speculation: why phase and precip lenses fail for Mombasa

**Mombasa has bimodal rainfall.** The long rains fall April–May; the short rains fall
October–November. These two peaks are roughly six months apart.

The `pre_concentration` variable is computed as a **unimodal circular statistic** — the
resultant vector of 12 monthly weights. When two peaks are ~180° apart on the circular axis,
their vectors nearly cancel. Mombasa's net vector is short (low concentration) and lands at
an angle determined by which rainy season is slightly stronger, not at either actual peak.

The consequence:

- **Precipitation regime** (`pre_mm_syr` + `pre_concentration`): Mombasa's low concentration
  score makes it look like a city with even, year-round rainfall — the opposite of what it is.
  European cities with gentle distributed rainfall (Augsburg, Salzburg) have similarly low
  concentration and end up as nearest neighbours.

- **Seasonal phase** (`pre_concentration` + `seas_phase_offset`): the phase offset between
  precipitation and temperature peaks is computed from the resultant vectors of both, so the
  precip angle is already wrong. Mediterranean cities, which have a single winter rain peak
  and a summer temperature peak, happen to share a similar *apparent* phase offset with
  Mombasa's mathematically distorted signal.

- **Temperature regime** (`tmp_dc_syr`, `tmp_seas_amp`, `tmp_concentration`) is unaffected
  because temperature in an equatorial city is both high and non-seasonal — the signal is
  unambiguous and unimodal statistics are appropriate.

**This is not a code bug.** The circular statistics implementation is correct. The problem
is that unimodal circular statistics are not appropriate for cities with bimodal rainfall,
and the WH Cities corpus contains a non-trivial number of equatorial cities that will
exhibit this artifact.

**The old PCA composite had the same blind spot** — low circular concentration (bimodal
tropical) and low circular concentration (hyper-arid desert) are indistinguishable to
unimodal stats — but it manifested as returning Arid/Desert cities rather than European ones.
Same root cause, different symptom.

---

## Comparison to sandbox similarity

The sandbox Similarity tab also uses `LENS_REGISTRY` + `find_similar()`, but at L06 and
against all 16,397 global basins. A direct comparison of Mombasa results across the two
surfaces would reveal whether:

(a) The bimodal artifact is worse at L08 than L06 (smaller basins, less averaging)
(b) The corpus restriction is the primary factor (254-city corpus has more equatorial options
    at L06 global level)
(c) The L06 thresholds return visibly wrong results for bimodal cities too

This comparison has not been run. Flagged for Opus review session.

---

## What needs resolving before WO1 can close

1. **Root cause confirmed or refuted** — is the bimodal circular-statistics hypothesis
   correct? Inspect Mombasa's `pre_concentration` and `seas_phase_offset` values in the L08
   index directly and compare against Augsburg, Split, George Town.

2. **Decision: accept as-is or fix** — options include:
   - Accept the limitation, label the lenses honestly ("not reliable for equatorial bimodal
     cities"), add a note to the panel
   - Add a bimodal flag / fallback for the precip and phase lenses
   - Drop precip and phase from the WH Cities dropdown, offer temperature only
   - Investigate a different circular-statistics approach (e.g. bimodal decomposition)

3. **Sandbox comparison** — run Mombasa on the sandbox Similarity tab (same lenses, L06
   global) and compare to confirm or refute the corpus-vs-global hypothesis.

---

## Status

**WO1 plumbing: complete.** Infrastructure is correct; the L08 index serves, the route
works, the UI renders.

**WO1 accept gate: not closed.** Temperature regime passes. Phase and precipitation lenses
fail the smell test for bimodal-tropical cities. Decision on remediation deferred to Opus
review session.
