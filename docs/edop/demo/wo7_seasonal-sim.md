# WO7 — Seasonality similarity query: notebook investigation + implementation

**Branch:** `demo_wo7` off `demo`
**Track:** 3 (Sandbox UI) + 2 (Features)
**Depends on:** WO6 closed — Seasonality tab live; six derived scalars in top-level `out`.

---

## Goal

Add a "Find similar seasonal patterns" capability to the Seasonality tab. User clicks a
button; the API returns a ranked list of gazetteer places whose containing basins have the
most similar seasonal signature to the query basin. Start with notebook investigation to
confirm assumptions before any production code is written.

---

## Part A — Notebook investigation

**Notebook:** `notebooks/edop/demo/wo7_seasonality_similarity.ipynb`

### A1 — Basin coverage by gazetteer

Load the 97k place gazetteer. Spatially join places to `basin06` (L06 first; L08 later if
warranted). Establish:

- How many L06 basins contain at least one gazetteer place?
- Distribution of place counts per basin (median, 90th percentile, max).
- What fraction of basins are empty (no gazetteer place)?
- Are the empty basins systematically in uninhabited regions (Sahara, boreal, polar), or is
  coverage sparse in regions of interest?

This sets expectations for how deep into the similarity ranking we need to go before
returning a useful result set.

### A2 — Distance metric

The two primary indices are `pre_concentration` [0–1] and `seas_phase_offset` [0–6]. These
are on different scales; raw Euclidean would weight offset ~6× more heavily than
concentration. Test three options:

1. **Normalized Euclidean** — z-score each index across all basins, then compute Euclidean
   distance. Simple; appropriate if the two indices are approximately uncorrelated.
2. **Mahalanobis (2-index)** — accounts for covariance between `pre_concentration` and
   `seas_phase_offset`. More principled if they co-vary significantly.
3. **Extended (4-index)** — add `tmp_concentration` and `tmp_seas_amp`. Check whether these
   add discrimination or dilute the signal.

Compute the correlation between `pre_concentration` and `seas_phase_offset` across all L06
basins. If |r| < 0.3, normalized Euclidean is adequate; if higher, Mahalanobis is warranted.
Report which metric the SF validation test (A3) responds to best.

### A3 — SF validation test

Query basin: the L06 basin containing San Francisco (pre_concentration ≈ 0.60,
seas_phase_offset ≈ 5.6 — confirmed Mediterranean-type).

Rank all L06 basins by similarity to the SF query basin using the best metric from A2.
Retrieve the top-N basins (start with N=50; adjust based on coverage findings from A1).
Join to gazetteer. Report:

- Which named places appear in the top results?
- Do canonical Mediterranean-climate regions dominate — central Chile, SW Australia,
  Western Cape, Iberia, Levant, California coast?
- At what rank does the first non-Mediterranean result appear?
- How many top-N basins contain no gazetteer place?

This is the primary validation. If the algo is working, the SF query should recover
recognizable Mediterranean-climate settlements before returning monsoon or maritime results.

### A4 — Threshold and result count

Determine a sensible cutoff for "similar enough to show":

- What similarity distance corresponds to a climatologically meaningful match vs. a
  best-available-but-poor match?
- How many results does a typical query return at that cutoff?
- Is a fixed top-N (e.g. 20 places) or a distance threshold the better UI contract?

Report a recommended default and the reasoning.

### A5 — L06 vs L08

If A1 shows L06 coverage is adequate (most top-N basins contain places), L06 is preferred —
smaller table, faster query, basin-scale smoothing already validated in WO5. If coverage is
sparse, repeat A1–A3 at L08 and compare. Report which level to use for the production query.

### A6 — Gazetteer place-type filter (if metadata available)

If the 97k gazetteer carries place-type or importance metadata, test whether a soft filter
(e.g. populated places above a size threshold, or excluding administrative boundaries)
improves result interpretability without significantly reducing coverage. Report whether
filtering is warranted.

---

## Part B — API endpoint

Based on notebook findings, implement a new endpoint:

```
GET /api/seasonality/similar?lat=...&lon=...&n=20
```

- Identifies the containing basin at the default level (L06 or L08 per A5 finding).
- Computes similarity distance from that basin to all other basins using the metric
  confirmed in A2.
- Joins top-N basins to the gazetteer, returning one result row per place (not per basin).
- Response shape (provisional — CC should adjust based on what the gazetteer carries):

```json
{
  "query_basin_id": 4120842,
  "metric": "normalized_euclidean_2idx",
  "results": [
    {
      "place_id": "...",
      "place_name": "Seville",
      "country": "ES",
      "lat": 37.39,
      "lon": -5.99,
      "basin_id": 4120900,
      "basin_rank": 3,
      "distance": 0.142,
      "pre_concentration": 0.58,
      "seas_phase_offset": 5.31
    },
    ...
  ]
}
```

Include the basin's own index values in each result so the UI can show why a place matched.

**Proviso:** The full pairwise distance computation across 16k L06 basins is trivial at
query time in Python (milliseconds). No precomputed distance matrix is needed unless
profiling shows otherwise. CC should confirm.

---

## Part C — Sandbox UI

Add a button to the Seasonality tab: **"Find places with similar seasonal patterns"**.

On click:
- Calls the new endpoint with the current location.
- Displays results as a simple ranked list: place name, country, distance score, and the
  two key index values for the matching basin.
- Optionally plots the matching places on the Map tab (if low implementation cost; not
  required).

No sophisticated UI at this stage — a readable list is sufficient. The goal is to see
whether the results are interesting, not to polish the display.

---

## Acceptance

- Notebook A3 (SF validation) recovers recognizable Mediterranean-climate settlements in
  the top results before non-Mediterranean results appear.
- API endpoint returns results in < 2 seconds for any query location.
- UI button triggers query and renders result list without page reload.
- All existing tests pass.

---

## Out of scope for WO7

- Regional heterogeneity query (Layer 3 from earlier framing) — separate future WO.
- Similarity across full EDOPS variable set (that is the WO4/WO6 Mahalanobis instrument,
  not this).
- Result map visualization beyond the existing Map tab — future WO if results prove
  interesting.
  