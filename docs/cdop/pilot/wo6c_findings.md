# WO6c findings — Similarity panel, rebuilt on the conjunction

**Work order:** `docs/cdop/pilot/wo6c_similarity-redux.md`
**Branch:** `cdop_wo6c` (cut from `cdop_wo6`). **Scope:** sandbox_v3.html Similarity tab only —
cdop_pilot's WH Cities dropdown has different requirements and is a later WO.
**Status:** in progress. Part D complete (2026-07-23). Engine + UI build not yet started.

This file is built incrementally. Part D was run first because it decides the temperature lens
definition before that lens is built (WO6c: "decide before building the temp lens").

---

## Part D — Does temperature get a shape term? — NO

**Notebook:** `notebooks/cdop/wo6c_partD_temp_shape.ipynb` (9 cells, all run 2026-07-23).
**Figure:** `output/cdop/wo6c_temp_corr_hist.png`.

### Question

Precipitation has monthly arrays and a shape term (correlation on the mean-centred twelve-value
curve) that discriminates — WO6b Part A, the backbone. Temperature also has monthly arrays, so a
shape term is *available*. But temperature cycles are far more uniformly sinusoidal than rainfall,
and every Northern-Hemisphere basin peaks in July. That is the kill condition precipitation escaped
(distribution massed near 1.0, no usable spread). Does temperature escape it?

**Decision rule (WO6c Part D):** if the pairwise correlation distribution saturates near 1.0 within
hemisphere, the temperature lens is `temp_level` + `temp_range` only, and `temp_shape` is excluded.

### Method

The WO6b Part A distribution test, run on temperature: pairwise correlation over a 4,000-basin
random sample split by hemisphere (Cell 5); per-probe rank decay (Cell 6); and — because temperature
has no arid gate — an amplitude-binned correlation check (Cell 7) to separate the two ways a shape
term can be worthless. Corpus: 16,338 valid L06 basins; no zero-variance temperature profiles.

### Results

**Temperature saturates within hemisphere — decisively (Cell 5).**

| | same-hemisphere | cross-hemisphere |
|---|---|---|
| pairs | 5,140,761 | 2,857,239 |
| mean r | 0.701 | −0.586 |
| median r | **0.963** | −0.835 |
| share > 0.90 | **63.3%** | 0.4% |
| share > 0.95 | **55.4%** | 0.1% |

Contrast WO6b precipitation, where ~86% of same-hemisphere pairs sat *below* 0.90 — that spread is
what let precip shape discriminate. Temperature is the mirror image: a two-spike distribution, same
hemisphere ≈ +1, opposite hemisphere ≈ −1, nothing to rank in between. The only real structure is
the cross-hemisphere anti-phase split, which is *phase* — already served by hemisphere / the
separate precip×temp correlation — not something a shape cut adds.

**Per-probe rank decay confirms it from the query side (Cell 6).** For the high-amplitude
extratropical probes the correlation barely falls across a thousand ranks, and a 0.95 cut admits
most of the corpus:

| probe | r@1 | r@1000 | spread | n≥.95 |
|---|---|---|---|---|
| Augsburg | 1.000 | 0.997 | 0.003 | 9,499 |
| Kaifeng | 1.000 | 0.998 | 0.002 | 9,554 |
| Yakutsk | 1.000 | 0.997 | 0.003 | 8,888 |
| Tbilisi | 1.000 | 0.996 | 0.004 | 9,460 |
| Tennessee | 1.000 | 0.998 | 0.002 | 9,503 |
| George Town | 0.971 | 0.762 | 0.209 | 12 |
| Nairobi | 1.000 | 0.852 | 0.147 | 112 |
| Mombasa | 0.999 | 0.912 | 0.087 | 270 |

The tropical probes (George Town, Nairobi, Mombasa) *appear* to discriminate — small n≥.95. That
apparent discrimination is noise, not signal, resolved by Cell 7.

**The amplitude split proves the tropical exception is noise (Cell 7).** Same-hemisphere pairs
binned by the smaller of the two seasonal amplitudes:

| amplitude bin (°C) | n pairs | mean r | median r | sd r |
|---|---|---|---|---|
| 0–1 | 94,166 | 0.179 | 0.175 | 0.360 |
| 1–2 | 393,439 | 0.113 | 0.215 | 0.524 |
| 2–5 | 748,562 | 0.020 | −0.027 | 0.639 |
| 5–10 | 732,633 | 0.641 | 0.805 | 0.373 |
| 10–20 | 1,439,370 | 0.938 | 0.975 | 0.097 |
| 20–100 | 1,732,591 | 0.984 | 0.990 | 0.015 |

Below ~5 °C amplitude the curve is noise: mean correlation ≈ 0, and in the 2–5 °C band the median is
−0.027 — a tropical basin is about as likely to anti-correlate with another tropical basin as to
correlate with it. Above ~10 °C it saturates. So George Town's and Nairobi's few matches in Cell 6
are noise-scarcity (noise does not reproduce, so almost nothing matches), not a coherent temperature
regime being selected.

### Verdict (Cell 9)

Same-hemisphere pairwise median 0.963 (> 0.90); median per-probe rank-decay spread 0.015 (< 0.10) →
**SATURATES**. `temp_shape` resolves PENDING_PART_D → **excluded**.

**The reasoning, in full.** A shape term must do two things to earn a slot: carry real signal (the
curve must describe the basin, not month-to-month noise) and discriminate (different basins get
meaningfully different correlation values). There is no seasonal-amplitude regime where temperature
does both:

- **Large swing (extratropics):** every same-hemisphere basin has the same single July/January-peaked
  cycle. Correlation is real signal but does not discriminate (median 0.963; a 0.95 cut admits ~9,000
  basins), and what little it distinguishes is already carried by the size of the swing (`temp_range`)
  and the hemisphere (phase). A shape term here is **redundant**.
- **Small swing (tropics, ~11% under 3 °C, Cell 4):** barely a cycle; the twelve values are
  dominated by noise. Correlation is **meaningless** (mean 0.02, median −0.027, sd 0.64) — measuring
  the agreement of noise.

Where the cycle is strong enough to be real it is the same everywhere in the hemisphere; where it is
weak enough to differ between basins the difference is noise. Either way it cannot do the work
precipitation's shape term does — which is precisely why precipitation shape is the backbone and
temperature shape is not.

**Consequence for the lens:** the temperature lens is `temp_level` + `temp_range`. The phase question
(hemisphere; rain-with-or-against-warmth) is served separately by direct precip×temp correlation
(WO6b Part E, Cell 19), not by a temperature shape term.

**Note on the a priori.** The extratropical half of this was close to a given — warm summers, cool
winters, one bump a year, sign-flipping at the equator. Running it earned its keep specifically at
the equator, where the tempting rescue ("the flat-temp tropics are a *distinct* regime shape could
pick out") is exactly the case Cell 7 kills as noise. The number, not the intuition, forecloses it.

---

## Draft lens schema (current — `temp_shape` removed)

Conjunction over typed conditions. Membership is `AND` across every condition; no scoring, no
compensation. The set is painted; size and spatial spread are reported; empty is honest scarcity.
Presets are anchor values — the panel control shows each band in its own units (±3 °C, 1.5×,
r≥0.90), not a strict/moderate/loose ladder (that ladder is retired). Terrain condition types are
deferred until the variable set is confirmed (WO6c Part C).

```json
{
  "_membership": "A candidate basin is IN the set iff it passes EVERY condition. No scoring, no compensation. Set is painted; size and spatial spread are reported; empty is reported plainly.",
  "_controls": "The panel control shows each band in its own units (±3 °C, 1.5×, r>=0.90). Presets are anchor values, not a strict/moderate/loose ladder — that ladder is retired.",

  "condition_types": {
    "precip_shape": {
      "quantity": "pre_mm_monthly, mean-centred 12-value curve",
      "test": "pearson(query, candidate) >= cut",
      "band_unit": "correlation cut",
      "presets": { "broad": 0.85, "default": 0.90, "tight": 0.95 },
      "caveat": "NOT a uniform quality bar: r=0.90 is rank 61 for Nairobi, rank 2,149 for Timbuktu (WO6b Cell 10b). Must be visible in panel copy."
    },
    "precip_magnitude": {
      "quantity": "pre_mm_syr, annual total",
      "test": "abs(log1p(candidate) - log1p(query)) <= log(ratio)",
      "band_unit": "ratio band (multiplicative; symmetric on log; immune to precip right-skew)",
      "presets": { "broad": 2.0, "default": 1.5, "tight": 1.25 },
      "note": "The accept-gate condition. By construction no set member falls outside it."
    },
    "precip_amplitude_cv": {
      "quantity": "cv = sd/mean of the 12-value precip curve",
      "test": "abs(candidate_cv - query_cv) <= width",
      "band_unit": "absolute cv, PER-QUERY band ONLY",
      "presets": { "broad": 0.25, "default": 0.15, "tight": 0.10 },
      "guard": "Never exposed as a global scalar (explodes on dry-season zeros). Self-protecting as a band: a low-cv query cannot reach high-cv arid territory. Cuts AFTER magnitude (WO6b Part D)."
    },
    "temp_level": {
      "quantity": "tmp_dc_syr, annual mean °C",
      "test": "abs(candidate - query) <= degrees",
      "band_unit": "absolute °C",
      "presets": { "broad": 4.0, "default": 3.0, "tight": 2.0 }
    },
    "temp_range": {
      "quantity": "tmp_seas_amp, max-min monthly °C",
      "test": "abs(candidate - query) <= degrees",
      "band_unit": "absolute °C",
      "presets": { "broad": 6.0, "default": 4.0, "tight": 2.0 }
    }
  },

  "lenses": {
    "climate.precip": {
      "group": "Climate", "label": "Precipitation regime", "status": "active",
      "conditions": ["precip_shape", "precip_magnitude", "precip_amplitude_cv"],
      "shade_by": "precip_shape"
    },
    "climate.temp": {
      "group": "Climate", "label": "Temperature regime", "status": "active",
      "conditions": ["temp_level", "temp_range"],
      "shade_by": null,
      "note": "No shape term (WO6c Part D: temperature saturates within hemisphere). Weakest lens standalone; exists mainly to compose the union."
    },
    "climate.union": {
      "group": "Climate", "label": "Climate (precipitation + temperature)", "status": "active",
      "conditions": ["precip_shape", "precip_magnitude", "precip_amplitude_cv", "temp_level", "temp_range"],
      "shade_by": "precip_shape",
      "note": "== the WO6b Part D validated five-condition conjunction. precip/temp lenses are SUBSETS of this."
    },
    "terrain": {
      "group": "Terrain", "label": "Terrain", "status": "proposed",
      "conditions": ["elev_level", "slope_level", "relief_level"],
      "shade_by": null,
      "note": "Scalar bands only — no curve, no shape term. Condition types deferred until the variable set is confirmed (WO6c Part C)."
    }
  }
}
```

---

## Parts A, B, C, E — engine + UI built (in review)

- **Engine** (`app/db/seasonality.py`): `find_conjunction` + `CONJ_LENSES`/`CONJ_CONDITIONS`, separate
  from the untouched `find_similar`. Conjunction index retains the mean-centred precip curve `Z`,
  `pre_total`, `cv`, `tmp_mean`, `tmp_rng`, rep points, arid mask (shape condition only). Route
  `GET /api/similarity/conjunction` (+ `/lenses`). Accept gate met: `tests/test_conjunction.py`
  reproduces all 33 WO6b Cell 16 union counts, Timbuktu attrition [2148,645,119,113,102], the
  magnitude-band gate, empty-is-honest, spatial spread. 6 tests green.
- **UI** (`sandbox_v3.html`, feature-flagged `SIM_CONJUNCTION`): painted set (members shaded by shape
  correlation; non-members unpainted — no pale outer wash), declared per-variable band controls
  (no strict/moderate/loose ladder), set-size + spatial-spread readout, honest-empty message,
  container line matching the Context tab. **Respects the L06/L08 toggle** (retires the old inert
  level control). Old composite panel stays in the DOM behind the flag.

## Review observations (browser + stats, 2026-07-23)

Held up under Karl's walkthrough; three things worth keeping:

- **The temp lens's selectivity rotates by query — it is not uniformly coarse.** SF's L08 basin has a
  *low* seasonal range (8.5 °C, the equable California coast), which is distinctive, so the ±4 °C
  range band is load-bearing and carves out a coherent global family — California, Baja, central
  Chile, the Cape, SW/SE Australia, New Zealand, Mediterranean Europe (2,366 basins). Tbilisi's L08
  range (22.3 °C) is common-continental, so its range band cuts little and the set is broad (6,338).
  WO6b Part D's "load-bearing condition rotates by query", now visible *inside a single lens*.
- **The L06/L08 toggle makes the container problem legible.** Tbilisi's temp set migrates south and
  contracts from L06 (basin mean 5.33 °C, Caucasus-dragged) to L08 (10.76 °C, more city-like) — the
  container effect shown as a before/after rather than stated as a caveat. The old panel ignored the
  level toggle; wiring it in turns the mountain-drag into a demonstrable affordance.
- **Large sets at L08 (render consideration, not a bug).** Temp-only at L08 can exceed the ~5,000
  WebGL budget WO5 set for the Context choropleth (Tbilisi 6,338). It renders, but the coarsest lens
  at the finest level is the worst case; precip/union stay small at any level. If it ever feels
  sluggish, the clean fix is a cap with a "showing N of M — tighten a band" note rather than
  auto-widening (which the honest-scarcity rule forbids). Logged; not capped.

## Candidate next lens condition — `precip_temp_phase` (surfaced in review, logged not built)

Karl's review of San Francisco under Precipitation regime at r≥0.95 exposed the honest limitation of
a calendar-locked shape term, and points to the condition that would complete it. **Logged here as a
candidate for the WO author (Opus) to weigh — not added to the schema; the design reasoning is
Opus's to make.**

**What was seen.** SF's L08 basin peaks in **January** (wet Nov–Mar, dry Jun–Aug — Mediterranean).
The r≥0.95 set spans 18,301 km and includes Southern-Hemisphere basins at lat −24° to −26° (southern
Africa, Paraguay/N. Argentina) that **also peak in January with r ≈ +0.995** — but there January is
high summer. These are *austral-summer-rain* basins, not Mediterranean. Verified directly on the
twelve-value curves (SF `[149,117,109,53,11,5,2,3,9,42,105,118]`; SH members peak-month J, r_vs_SF
+0.994…+0.995).

**Why.** Shape correlation is calendar-locked (no circular shift — WO6b Part E) and therefore
**hemisphere-blind**: it cannot separate SF's cool-season (winter) rain from the Kalahari's
warm-season (summer) rain, because both fall in Dec–Feb. Not a defect — the documented behaviour of
a shape measure. The union lens does not fix it either: `temp_level`/`temp_range` are level/range
bands, not the rain-relative-to-warmth phase, so a summer-rain SH basin with SF-like temperature
level and range still passes.

**The condition that would separate them** is the precip×temp phase — Karl's own
**{warm-wet / cool-dry / neither}** axis — served by the direct correlation of the 12-month precip
curve against the 12-month temperature curve (WO6b Part E, Cell 19; verified there: 7/7 sign
agreement with `s_d`, defined for the 2,694 bimodal basins `s_d` cannot handle). SF scores strongly
**negative** (rain against warmth → cool-wet Mediterranean); the SH summer-rain twins score strongly
**positive** (rain with warmth). A `precip_temp_phase` condition — a band or sign gate on that
correlation — would collapse the SF set to genuine cool-season-rain basins and drop the hemisphere
doubles. It is the natural completion of the two-discrete-classes target; deferred to Opus.

See also `docs/design/deferred_items_register.md` § CDOP — similarity.
