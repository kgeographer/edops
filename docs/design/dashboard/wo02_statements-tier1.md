# WO-02: statement inventory, tier 1 (single-payload statements)

Prepared 2026-10-29 for CC. Depends on: `sandbox_cheatsheet.md` (verified against v0.4.2, `a673660`).

## Purpose

Find out, empirically, what true statements and graphs can be derived by rule from one signature payload, and which of them the Sandbox does not already show. This is an inventory of what is computable and stable. It is **not** a decision about what is worth saying, and it does not design the dashboard.

The rule-based layer will be used where a user cannot be expected to read a raw signature. Everything it says must come from payload fields, with no LLM.

## Scope

**In:** tier 1, statements that need only the `/api/areas` payload for one query (single basin, buffer, polity; Band T where requested).

**Out (later work orders):** tier 2 (statements that need Context, Similarity, the public basin call or the Seasonality indices), tier 3 (statements that combine several queries: L6 vs L8, ring centre vs neighbours, HYDE across epochs). The friendly-name crosswalk for variables is its own work order.

## Constraints that govern every rule

1. **Describe, do not judge.** A statement reports a position, a distribution, a gap or an absence. No verdicts, no "unusual", "significant", "good" or "poor".
2. **No cutoff is set by looking at cases.** Any soft quantifier ("most", "about half", "close to") must be tied to a number printed beside it, and must be swept over a range of plausible cutoffs (see Sweep rule). The cutoffs in cheat sheet §9 are the existing baseline, not authority.
3. **Branch on `method`, `status`, `score_suppressed`, `coherence` and scope**, never on a null score alone (cheat sheet §2.6).
4. **State the reference frame.** A percentile is "ranked against all L6 (or L8) basins worldwide"; for areas it is an area-weighted mean of member percentiles.
5. **Respect what a scope cannot give.** Multi-basin rows have no native-unit value; polity discharge is `not_areal`; Band T has no percentile; polity modality is skipped by design.
6. **Zero-inflated variables are different.** When the variable's global zero fraction is at least 0.20 the percentile is zero-aware (cheat sheet §2.5): 0 means absent, otherwise rank among non-zero. Rules must branch on this.
7. **Percentile direction.** For continuous variables a higher percentile means a higher value; categoricals have no percentile.

## Step 0: fixtures (Karl approves before anything is harvested)

Propose two sets and give a one-line reason for each member.

**A. Coverage fixtures** (about 20 to 30 queries). Selected to cover conditions, not to illustrate cases. Each condition below needs at least one query; CC picks the places.

- arid, humid, and mountain terrain; coastal, inland, endorheic; exogenous-water (upstream wetter than local)
- L6 and L8 for at least three places
- single basin; buffer small (fewer than 5 basins, so coherence is cleared) and large; polity with a one-year slice and one with a long slice; a polity at L8 (crosswalk path)
- Band T: a CE span with LMR coverage, a BCE span (HYDE nearest-epoch case), a span with no LMR, a span with and without eVolv2k events
- low-coverage stress cases from cheat sheet §4 (Rome 200 km, Caspian shore 150 km, Greenland 300 km)
- at least one query that produces each status value and a suppressed score

**B. Population sample** (a few hundred single-basin and buffer queries). A random, stratified sample of land points (stratify by climate zone or continent; document the method). Its job is to give the **distribution of every derived statistic across the world**, so cutoffs can be argued from populations and not from fixtures.

Deliver the proposal as a table (query, scope, level, bands, span, condition covered). Wait for Karl's approval.

## Step 1: persist payloads

- Save the **full** payload for each approved query (`detail=true`, untrimmed), never edited.
- Location and layout are CC's call. Requirements: one file per query; a manifest recording the exact request, scope, level, bands, span, capture date, app version and commit; and a refresh script that regenerates everything from the manifest.
- Payloads are read-only inputs to the notebooks. The notebooks never call the API.
- Report the location and size to Karl when done.

## Step 2: field-availability matrix

First notebook, before any statements. For every field named in cheat sheet §2.3 (and `detail` keys), tabulate where it is present by scope x method x status. This is the ground truth for what a rule may rely on. Flag any field the cheat sheet describes that the payloads do not carry, and any the payloads carry that the cheat sheet does not describe.

## Step 3: statement families

One notebook per family, over fixtures first, then the population sample. For each statement type produce a row in the master table (below) and at least one draft sentence from a template with named slots.

| Family | Statement types to test (add others you find) |
|---|---|
| Position | percentile with reference frame; raw value and units (single basin only); zero-aware branch (absent vs rank among present) |
| Distribution | headline percentile with core window; core share as a printed number; p10 to p90 range; min to max; split (tied score plus separate group); small-n (fewer than 5 basins) |
| Categorical | modal class and share; full mixture (top n classes, residual); mixed vs concentrated; low-coverage wording |
| Empty cells | one sentence per status (`outside_active_domain` one vs several basins, `no_data`, `not_areal`, `low_coverage`, suppressed) |
| Local and upstream | the gap between a local row and its `_upstream` pair, in percentile points; agreement vs divergence; pairs where only one exists |
| Within-band families | soil texture (clay, silt, sand sum near 100; do not treat as independent); discharge triple; wetland groups; other families CC identifies |
| Cross-band | which variables sit furthest from the global median, by percentile distance, within a band and across bands |
| Coverage and shortfall | `coverage`, `shortfall`, `n_units` per row, `marginal_exposure` for polities |
| Band T | LMR: sign and size of anomaly, spread across cells, `low_resolution` cases; HYDE: totals per epoch, nearest-epoch distance; eVolv2k: event count, size, and timing relative to the span |

## Master table (the main deliverable)

One row per statement type, as a markdown or CSV file kept with the notebooks.

| Column | Content |
|---|---|
| id, family, name | |
| inputs | payload fields used |
| rule | plain-language rule; short pseudocode only where logic is subtle |
| applies to | scopes, levels, bands, methods, statuses |
| does not apply when | including the reason |
| template | sentence(s) with named slots |
| in UI today? | yes/no and where (cheat sheet section) |
| needs new data? | any field not in the payload (feeds tier 2 or an engine change) |
| fixture result | applied / not applicable / error, and notes |
| population result | how often it applies; distribution of the statistic |
| sweep result | stable / flips, and over what range |

## Sweep rule

For any statement that depends on a cutoff, evaluate it over a grid of plausible cutoffs across the population sample and record the share of queries whose wording changes. A statement is **stable** if its wording does not change across the range. If it flips, mark which variables and scopes flip and fall back to stating the number alone. Do not choose a cutoff; report the sensitivity.

## Check-ins

1. After Step 0: fixture proposal to Karl.
2. After Step 2: field-availability matrix, with any discrepancies against the cheat sheet.
3. End: the master table, the notebooks, and a one-page summary of what is computable, what is already in the UI, what is new, and what is unstable.

## Not in this work order

Changing any app behavior or threshold; designing dashboard screens; LLM generation; friendly-name crosswalk; tiers 2 and 3. Any discrepancy found in the cheat sheet goes into a short list at the end of the summary, not into a separate alignment pass.
