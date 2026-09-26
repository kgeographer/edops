# Regional layers: framing for historical-period expansion

**Status:** framing doc, pre-phase. It sits alongside `drought_atlas_memo.md`, which covers
the first concrete layer. Written 2026-09-26 against `main` @ `4d06e04`.

---

## 1. Why regional, and why now

EDOPS so far draws only on global sources: BasinATLAS, LMR, HYDE and eVolv2k. For historical
periods those sources thin out quickly:

- **LMR.** Proxy density collapses before ~700 CE. The Sandbox already floors its LMR maps at
  700 CE (`routes_sandbox.py` `lmr_values`), and EDA shows event timing blurring in
  sparse-network regions (Samalas at Kaifeng vs. Central Europe).
- **HYDE.** Land use before 1700 is largely *modelled* from population estimates, and is
  centennial or coarser before 1700.
- **eVolv2k.** A global forcing record. It tells you nothing about local response.

The strongest historical environmental evidence is regional:

- tree-ring drought atlases
- documentary weather series
- pollen-based land cover
- lake and speleothem records

A global-only EDOPS therefore stays thinnest exactly where its historian users need it most.
Going regional means accepting that EDOPS knows **different amounts about different places at
different times**. The design task is to make that unevenness *visible and informative*
rather than hidden or apologised for.

---

## 2. Principles

These carry over from the drought memo, generalised:

1. **Global floor, regional ceiling.** Global layers stay everywhere. Regional layers are
   added beside them, never substituted silently.
2. **Provenance travels with every value:** layer id, version, native kind, season,
   resolution, and skill for the requested span.
3. **No cross-layer blending.** Overlapping layers are returned side by side, with a declared
   precedence. EDOPS does not synthesize new reconstructions.
4. **Absence is a status.** The engine's Pin 1 vocabulary already covers the two cases:
   - `outside_active_domain`: the place is outside the layer's footprint.
   - `no_data`: inside the footprint, but outside the layer's time range.
5. **Comparability comes from ranking each value within its own record, not raw units.**
   Regional values are compared through their position within their own record ("dry *for
   here*"). This generalises the 850–1850 re-baselining the Sandbox already applies to LMR.
6. **Global instruments stay global.** Similarity lenses, global percentile scores, LISA and
   the Explorer's global ranking all assume every basin has a value. Regional layers are kept
   out of them, or used strictly within-domain, flagged as such.

---

## 3. Registry

A single registry covers all regional (and, retroactively, global temporal) layers. This
generalises `tda_layer` from the drought memo. If this framing is adopted, create the
generic registry directly rather than an atlas-specific one.

```
temporal.layer_registry
  layer_id        text PK        -- 'owda_v1', 'cn_drywet_v1', 'reveals_eu_v2', 'lmr_v21', …
  theme           text           -- 'hydroclimate' | 'temperature' | 'land_cover' | 'hydrology' | 'connectivity'
  kind            text           -- display/aggregation type, see §4
  scope_class     text           -- 'global' | 'regional' | 'site'
  variable        text, units text, season text
  resolution      text           -- '0.5°', 'station', '500-yr windows', …
  year_min int, year_max int
  footprint       geometry(MultiPolygon, 4326)   -- where the layer can speak at all
  skill_model     text           -- 'per_cell_nests' | 'per_station' | 'none_published' | …
  precedence      int            -- within theme, where footprints overlap
  citation, doi, licence, notes  text
```

Per-kind value tables sit under it:

- **Grid cells:** as in `tda_cells`.
- **Stations or sites:** point geometry plus series.
- **Event rows:** as in `evolv2k_v4`.

Registering the existing layers (LMR, HYDE, eVolv2k) in the same table costs almost nothing.
It means the coverage surfaces in §5 can show global and regional layers in one grammar.

The registry also becomes a documentation source. `generate_codebook.py` could read it next to
the variable catalog, and `docsite/data-sources.md` could get a generated coverage table.

---

## 4. Kinds: a closed set of shapes and display rules

Each kind has one aggregation rule and one display rule, so adding a dataset never means
designing a new chart. The engine's `method` field already carries `grid_areal_distribution`
and `global_forcing`. The proposed kinds extend that vocabulary:

| kind | Example layers | Aggregation over a query area | Display rule |
|---|---|---|---|
| `grid_field` | LMR, drought atlases, European seasonal fields | fractional-overlap weighted mean (existing `grid_areal_distribution`) | line series + within-record percentile |
| `grid_extensive` | HYDE, pollen-based land cover | overlap-weighted sum (existing HYDE path) | stepped series at native epochs |
| `station_series` | Chinese dryness/wetness stations, nilometer | none: **nearest station within a max distance**, distance reported | line series labelled "nearest record: X km" |
| `ordinal_index` | 5-grade dryness/wetness, documentary indices | modal class + class distribution | class-coloured strip (grade bands, not a line) |
| `event_catalog` | eVolv2k, documented floods and famines | events within span (and footprint, if regional) | markers on the shared timeline |
| `site_proxy` | SISAL speleothems, Neotoma pollen sites | nearest *n* sites within radius, never averaged | small multiples, with distance and resolution per site |

Two rules matter most here:

- `station_series` and `site_proxy` are **not areal**. They answer "what is the nearest
  evidence?", never "what was the value here?". The payload must carry the distance, and the
  surface must show it.
- `ordinal_index` is never averaged into a number. A grade-3 mean of grades 1 and 5 is
  meaningless.

In `make_row` terms, each new kind is a new `method` value and `unit_type`, with the distance
or class detail inside `detail`. The payload contract changes only by adding vocabulary.

---

## 5. Surface: coverage as the headline

### 5.1 Coverage strip (per place): the key new component

A compact timeline with one row per layer that applies at the queried place. Bars span the
layer's valid years there, shaded by skill, with the query span overlaid. Rough mockup,
Kaifeng basin:

```
                  0      500     1000    1500    2000 CE
                  |-------|-------|-------|-------|
query span 965–990                  ▮
LMR v2.1 (2°)     ·······░░░░░░▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓|      ░ low  ▒ mid  ▓ high skill
MADA v2 (1°)                         ▒▒▒▓▓▓▓▓▓▓▓▓|      starts ~1000: query falls before it
CN dry/wet grade                             ▓▓▓▓▓|      station 38 km away, from 1470
HYDE 3.4          ▏   ▏   ▏   ▏   ▏  ▏ ▏ ▏▏▏▏▏▏▏▏||     epochs (modelled pre-1700)
eVolv2k           ▴      ▴  ▴     ▴  ▴▴   ▴  ▴  |       global events
```

What it does:

- **Explains empty results before they are read.** You can see why Kaifeng 965–990 has no
  atlas value: the query sits before MADA's bar starts.
- **Shows the unevenness honestly** in one glance, without prose disclaimers.
- **Doubles as navigation.** Tapping a row opens that layer's detail; dragging the span
  handle re-queries.
- **Works on a phone.** It is a stack of thin horizontal bars.

It would sit at the top of the Sandbox Band T panel for Settlements and Polities alike. For
Polities, bar shading could also encode `coverage_frac` (the share of the polity the layer
covers).

### 5.2 Footprint map (world)

In Explorer's Global tab, an overlay of layer footprints: filter by theme, and scrub a year
to see which footprints are "live" in that year. It answers "where and when does EDOPS know
more?" The same registry feeds it, so it stays current automatically.

### 5.3 Band T panel: progressive disclosure

The panel grows past what fits once there are five or more sources per place. Three tiers:

1. **Coverage strip** (always shown).
2. **One headline per theme.** Hydroclimate, temperature and land use each show their
   preferred layer's series or class strip, plus the within-record percentile.
3. **Per-layer detail on demand:** alternative layers, skill, distribution, provenance.

The existing Sandbox tabs (PDSI / Temp / Precip / eVolv2k) map naturally onto tier 2 as
themes rather than as sources.

### 5.4 Explorer choropleths

Grid kinds get basin choropleths through the settled PMTiles + flat-values pattern, with
basins outside the footprint shown in neutral grey. Station, site and ordinal kinds are
point layers over the choropleth rather than basin fills; filling basins from a station
would be exactly the false areal claim ruled out in §4.

### 5.5 API

- **`/api/coverage?lat=&lon=` (or `&geom_wkt=`).** Returns the strip's data: applicable
  layers, per-place valid years, skill segments and distances. This is cheap and
  registry-driven. The Sandbox calls it on resolve, before the signature request.
- **The public `/signature` contract grows only additively.** New Band T rows carry new
  `method` and `unit_type` values, and `meta.data_sources` lists the layers that contributed.

---

## 6. Candidate layers

Every row needs checking (format, licence, access). None was verifiable from the session
that wrote this.

| Layer | Theme | Kind | Region | Span (approx.) | Why it matters |
|---|---|---|---|---|---|
| Drought atlases (OWDA, MADA, LBDA, MXDA, ERDA, ANZDA, SADA) | hydroclimate | grid_field | N. America, Europe–Med–ME, Monsoon Asia, Australia, S. America | 0–2012, varies | first layer; see `drought_atlas_memo.md` |
| PHYDA | hydroclimate | grid_field (global) | global | 1–2000 | seasonal global drought floor alongside LMR |
| Chinese dryness/wetness grade charts | hydroclimate | ordinal_index / station_series | Eastern China (~120 stations) | ~1470– | dense documentary record where LMR is weak |
| REACHES | weather events / hydroclimate | event_catalog → ordinal | China | Qing (1644–1911) | high-resolution documentary detail |
| Euro-Climhist / tambora.org | hydroclimate, temperature | event_catalog / ordinal | Central Europe; multi-region | medieval– | documentary indices + extreme events |
| Roda nilometer | hydrology | station_series | Nile basin | 7th–15th c. (gaps) | one series speaking for a whole basin |
| European seasonal fields (Luterbacher temp; Pauling precip) | temperature, hydroclimate | grid_field | Europe | ~1500– | seasonal resolution; complements JJA atlases |
| Pollen-based land cover (REVEALS Europe; LandCover6k) | land_cover | grid_extensive | Europe; expanding | Holocene, coarse windows | an evidence-based check on HYDE's modelled land use |
| SISAL speleothems | hydroclimate | site_proxy | global but patchy | Holocene+ | only evidence in some regions (e.g. parts of Africa, SW Asia) |
| Neotoma pollen sites | vegetation | site_proxy | global but patchy | Holocene | raw site evidence behind the reconstructions |
| Itiner-e / DARMC Roman roads | connectivity | vector (new kind) | Roman world | Roman period | "place" as connectedness; a first non-climate layer |

The last row would need a seventh kind (network or vector), which is why it is listed but
not sequenced.

---

## 7. Sequencing

1. **Registry + `/api/coverage` + coverage strip.** Seed the registry with the existing
   global layers (LMR, HYDE, eVolv2k). This is useful on its own: it already explains the
   LMR 700 CE floor and HYDE's modelled early epochs better than notes do.
2. **Drought atlases** (`drought_atlas_memo.md` WO0–WO3). The first `grid_field` regional
   layer, which exercises `outside_active_domain` / `no_data` and overlap precedence.
3. **One ordinal/station layer.** The Chinese dryness/wetness grades are the obvious
   candidate. They exercise the non-areal kinds and the nearest-evidence surface, and they
   cover Kaifeng.
4. **Surface consolidation:** the three-tier Band T panel and the Explorer footprint map.
5. **Breadth by theme:** pollen land cover, European seasonal fields, speleothems.

The ordering lets you build the surface problem's solution (steps 1 and 4) against real
heterogeneity (steps 2 and 3), not in the abstract.

---

## 8. Questions for Karl

1. **Registry scope.** Register the global layers too, so one coverage grammar spans
   everything? This framing recommends yes.
2. **Nearest-evidence semantics.** What maximum distance makes a station or site record
   "about" a place? Should it be fixed, per kind, or user-set?
3. **Ordinal layers in the public API.** Expose raw grades, or only within-record
   positions?
4. **Band T naming.** Once themes replace sources in the panel, does "Band T" stay one band
   with themed sub-blocks, or split (e.g. T-hydro, T-land)?
5. **Scope of "environmental".** Do connectivity layers (roads, rivers as routes) belong in
   EDOPS, or in the deferred CDOP?
