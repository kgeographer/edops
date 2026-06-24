# Contract amendments — running record

*The durable home for drift between the response contract and what's been built. The instant a
contract item is flagged, it gets a row in **Pending** — by whoever flags it, same turn. At an
amendment pass, Pending items are folded into the contract doc, then moved to **Folded** with
the date. This file is the audit trail; the contract doc is the standing reference. Mirrors the
deferred register's discipline, applied to contract drift instead of deferred work.*

---

## Pending (not yet in the contract)

| Item | Status |
|---|---|
| **distribution_only coherence** — distribution_only populates `representative_score` but emits `coherence=null`, so its lean row carries a headline with no trust flag — the one place the self-trusting-lean-row principle isn't met. `coherence` is a pure spread test (weighted p90−p10 < T) that B5 already computes, so it's free to emit. Opus recommends emitting it. | **Open decision** — carried into contract §7 as the single open item; settle at the post-WO10 consistency pass. |

---

## Folded — 2026-06-23 (post-WO9 amendment pass)

The seven that accumulated across WO4–WO9, plus three clarifications declared in the same pass.

| # | Item | Where folded |
|---|---|---|
| 1 | **Single `&detail`** — `&dists` dropped; one projection switch covers distributions, regimes, temporal detail. | §6 (table + prose); §7 |
| 2 | **Synthetics → catalog** — `outlet_type`/`coast_fraction` are catalog-resident derived rows (built WO7b), provenance in the catalog `notes` column. Retires the draft's "synthetic with no catalog row / `derived_from` on the row" framing. | §3; §7 |
| 3 | **Resolution-vs-decimation** — HYDE epoch-snapping (lossless resolution) vs LMR notch-averaging (forbidden decimation). | §6 *(already present in uploaded copy; confirmed kept)* |
| 4 | **Four envelope pins, final form** — status value set `{ok, outside_active_domain, no_data}`; caveat shape (`caveat` list on row, `caveats` dict at top level); two-collapses orthogonality; `modality ∈ {unimodal, two_regime}` with `suppressed` dropped and `score_suppressed` added. | §2, §4, §6, §8 |
| 5 | **Modal label in lean row** — `class_mixture` carries the modal class label in `representative_raw` (WO7b). | §4 |
| 6 | **Null-score reasons are four, not two** — `spread` (coherence), `two_regime` (score_suppressed), Band-T (band), categorical/flag (method); each distinguished by another field. | §4 |
| — | *Clarification:* **n_units for selection methods** — `n_units` reports the resolved set size; for `dominant_basin`/`extreme` the carrier unit is in `detail`; nothing branches on the distinction (settled WO5). | §4 |
| — | *Clarification:* **Band T row fields** — Band T rows additionally carry `year`, `epoch_year`, `units`. | §4 |
| — | *Clarification:* **Blessed deviations** — three rows deliberately depart from the frozen TSVs where the engine corrects a notebook omission, each re-frozen with sign-off: LMR caveat (WO4), perennial flag (WO5), modal label (WO7/7b). | §9 |

---

## Discipline

1. Flag a contract item → it gets a Pending row the same turn, written here, never "on the pile."
2. At an amendment pass, fold Pending into the contract doc and move each to Folded with the date.
3. Run a pass whenever Pending grows past a couple of items — drift compounds, and the most delicate build is the worst one to do against a stale contract.
