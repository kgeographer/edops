# CC Work Order — Areas Step 3, Block 3: Categorical aggregation (% of class)

Branch: `areas_step3`. Fixture: Timbuktu 100 km / L06 buffer (same weighted basin set
used by Blocks 1–2). Goal: for every categorical signature variable, collapse the buffer's
weighted basin set into a class-mixture, a modal class, and a concentration verdict, conforming
to the shared output envelope so downstream signature composition can read it uniformly.

This block does NOT score categoricals (no percentile, no rarity). `position_method` is the
point-signature scorer and is irrelevant here. Aggregation is class *membership* only.

## Confirm before coding (do not assume)

1. **Buffer set source** — the Step 1 resolver output file for Timbuktu (weighted basin set:
   `hybas_id`, `weight`, weights sum to 1 over land; geographic `shortfall` reported separately).
   Use the same file Blocks 1–2 read. Confirm its name and columns.
2. **`step2_class_ids.tsv` content** — confirm each cell holds the **integer class id** (fetched
   from the raw table via `db_col`), not the view's text label. Block 3 groups on the id.
3. **Label source per variable** — `class_id → name` comes from the BasinATLAS `lu_*` lookup
   tables, the same join the signature views use. Confirm where the per-variable pointer lives
   (view DDL and/or catalog cols `basin08_col_s` / `atlas_id`); build a `{var: {id: label}}` map.
4. **NoData sentinel per variable** — confirm how "no class" is encoded (NULL vs -999 vs 0).
   Do NOT assume 0 means missing — 0 is a valid class for some BasinATLAS fields. Resolve per
   variable before the renormalize step.
5. **`step3_results.tsv`** — confirm it exists from Blocks 1–2 and append Block 3 rows to it
   under the same envelope (merge, no duplicate `variable` rows).

## Variable set

Source from the catalog: `type in {string, integer}` AND `position_method == 'rarity_rank'`,
then **exclude** `coast_flag` (Block 4) and `pnv_shares` (deferred — compositional object, see
register). Expected 12 vars: lithology, wetland class, climate zone, climate stratum, biome,
terrestrial ecoregion (id + name), PNV majority, freshwater habitat, freshwater ecoregion,
land cover, outlet type.

`typology_cluster` is NaN for all of these — that is expected; categoricals dispatch by type,
not typology. Where a classification appears as both `_id` and `_name` (terrestrial ecoregion),
aggregate it **once** on the stable key and attach the label; do not double-count.

Add a Cell-1 assertion that `coast_flag`, `endorheic`, and `pnv_shares` are absent from the
working set.

## Constants

| Const | Value | Note |
|---|---|---|
| `PLURALITY_THRESHOLD` | 0.85 | provisional; high on purpose (bias toward "mixed" — preserve heterogeneity); calibrate against more fixtures later |
| `MIN_SHARE_EPSILON` | 1e-6 | drop sliver classes below this from the mixture and from `n_classes` |
| `LEVEL` | `L06` | current results are L06 only |

## Cells

**Cell 0 — config.** Branch/path setup; derive output dir from module location
(`output/edop/areas/`); declare constants; `dtype={'hybas_id':'int64'}` everywhere.

**Cell 1 — load + guard.** Read buffer set, `step2_class_ids.tsv`, catalog — all via
`db_utils.read_areas_tsv`. Build the Block-3 variable set per the rules above. Assert flags /
deferred vars excluded. Build the `{var: {id: label}}` lookup from `lu_*`.

**Cell 2 — aggregate per variable.** For each variable:
- Join class ids to the buffer set on `hybas_id`.
- Drop basins whose value is the confirmed NoData sentinel for that variable; record dropped weight.
- `coverage_weight` = (sum of surviving basin weights) / (total land weight of the buffer set).
  This is the per-variable **data-absence** coverage — distinct from the buffer's geographic
  shortfall. Renormalize the surviving weights to sum to 1 *within the surviving set* before
  computing proportions.
- Group surviving basins by class id; sum renormalized weights → proportion per class.
- Drop classes below `MIN_SHARE_EPSILON`; attach labels; sort descending.

**Cell 3 — modal + verdict.** Per variable: `modal_class_id` / `modal_share` / `modal_label`
= argmax; `n_classes` = classes above epsilon; `concentration` = HHI = Σ(pᵢ²) (carried as a
continuous detail); `verdict` = `concentrated` if `modal_share ≥ PLURALITY_THRESHOLD` else `mixed`.

**Cell 4 — assemble outputs (in memory, no writes yet).**
- Headline rows (one per variable) for `step3_results.tsv`, shared envelope:
  `variable` (schema_key), `method='class_mixture'`, `status` (`ok` | `low_coverage` if
  coverage_weight below a floor — propose 0.5, flag for review), `representative_score=NaN`,
  `representative_raw=modal_label`, `n_basins` (surviving count), `coverage_weight`.
  Block-3 detail cols: `modal_class_id`, `modal_share`, `n_classes`, `concentration`, `verdict`.
- Long companion `step3_block3_mixture.tsv`: rows `(variable, class_id, class_label,
  weight_fraction)` — the full mixture, all variables stacked.

**Cell 5 — validation (print, do not write).**
- Per variable, Σ `weight_fraction` ≈ `coverage_weight` (atol 1e-6).
- No duplicate `variable` rows in the headline; no NaN class ids; all `hybas_id` int64.
- Timbuktu spot checks: print top-3 mixture per variable; climate zone should be dominated by a
  hot-desert/arid class, land cover by bare/sparse, biome by desert/xeric. Flag anything that
  isn't directionally sane.
- Confirm `coast_flag` / `endorheic` / `pnv_shares` absent from outputs.

**Cell 6 — write (gated).** Only after the Cell-5 summary is reviewed: append headline rows to
`step3_results.tsv` (merge, dedup on `variable`) and write `step3_block3_mixture.tsv`.

## Done = 

`step3_results.tsv` carries 12 new `class_mixture` rows alongside Blocks 1–2; the companion
mixture table validates (sums match coverage); Timbuktu's modal classes are geographically
sane; flags/deferred vars confirmed out.
