# The Workbench Societies panel: a précis (draft for Opus)

Draft of 17 Nov 2026, compiled by CC from the repo's records (WO8a to WO8d, CITYKIN WO4, the 10 Aug 2026 session log, the Workbench docsite page, `workbench.html`). Not yet read by Karl. Sources are listed at the end; numbers are taken from those documents, and anything I did not re-derive is marked. The statistics live in notebooks; the panel itself only displays.

## 1. What the panel is for

The Societies tab of the Workbench (`/workbench`) asks whether a cultural trait coded for a society tracks the environment that society lives in, and how far shared language ancestry and cultural contact can account for the pattern instead. It works on the Ethnographic Atlas (D-PLACE, Murdock et al. 2025): 1,291 societies coded on 94 variables, mostly for the "ethnographic present" (focal years 1850 to 1940). Each society is a point that stands for a territory. 1,133 of them (87.8%, in 971 distinct Level 08 basins) are joined to an EDOPS basin signature; the other 158, mostly islands and coasts, are dropped from every environmental analysis.

Two traits are wired, chosen at the start of the WO8 arc as one of each kind:

- **EA042, dominant subsistence** (foragers, pastoralists, farmers, and so on). Environment has a named theoretical hook here (water for rain-fed agriculture, temperature as a softer gradient), so the display is **confirmatory**.
- **EA034, high gods** (from absent, through "otiose", to "active but not supporting morality", to "active and supporting morality"). There is no predicted environmental axis, so the display is **exploratory** and says so.

## 2. What the panel displays

Choosing a trait value highlights the matching societies on the map. Beside the map it offers:

- **Climate envelope** (EA042): the chosen societies plotted by aridity against temperature, the two axes that WO8a found separate subsistence most cleanly.
- **Environment scan** (EA034): five plain-word strips (aridity, temperature, seasonality, ruggedness, landform position, each with named poles such as Arid to Wet). Each society is one tick at its own percentile against all 1,133 basin-joined societies. There is no composite score and no significance language on the page; a deliberate rule from the WO4 redesign is that "tighter than X% of random draws" never appears in the interface.
- **A language-family donut** (families named from Glottolog, with an Other bucket and an Unresolved bucket), hover-linked to the map, the scatter and the strips. Hovering a family lights up its societies everywhere, which makes shared ancestry and independent recurrence visible side by side. Family is labelled, not removed.
- **Ecoregions by realm**: which OneEarth ecoregions the chosen societies fall in (a descriptive default).
- **Isolates** (EA034 only, experimental): each society ranked three separate ways against others holding the same trait value: ancestral (how rare the value is in its own language family), geographic (distance to the nearest unrelated-family holder) and environmental (distance in five-variable space to the nearest holder). No combined score and no threshold; the order is the output, and where the three disagree is the interesting part. The help text states what a high rank does not establish: the outer edge of a diffusing practice looks the same as independent invention.

## 3. The analysis underneath (done in notebooks, not on the page)

The WO8 arc (July 2026) was notebook-only by design. It asks whether a trait covaries with environment **net of shared ancestry**, using a hand-rolled, unit-tested distance-based engine (`scripts/cdop/dbperm.py`: PERMANOVA, db-RDA, Freedman-Lane partial tests, PERMDISP for dispersion) and, for the exploratory work, `distance_core.py`. The control for Galton's problem is a **permutation restricted within language family** (a Glottolog crosswalk covering 92.6% of societies): shuffle which society holds which value only among relatives. A "noise ceiling" (the 95th percentile of the permutation null) was fixed before the political-complexity result was seen.

| WO | Trait | What was found |
| --- | --- | --- |
| 8a | EA042 subsistence (positive control) | Separates cleanly in a **climate envelope** (aridity, precipitation, runoff, temperature, seasonal amplitude). **Environment sets outer bounds on culture and does not determine it**: one near-hard wall (water for rain-fed agriculture), one soft gradient (temperature). Rainfall seasonality is orthogonal. |
| 8b | EA030 settlement fixity (918 societies) | Strong at face value (R2 about 0.21) but about 84% of it is subsistence in disguise; net of subsistence the residual is negligible (R2 0.01 to 0.03). Sedentary societies concentrate in a narrow favourable band (wet, warm, equable); mobile ones range widely. The family control **bit exactly where predicted**: temperature level collapsed under it (p = 0.020) while aridity (p = 0.0005) and thermal seasonality held. |
| 8c | EA033 political complexity | The raw link to climate is weak (R2 = 0.05). The tiny residual clears its noise ceiling but is not separable from the subsistence and settlement overlap (states are about 92% intensive agriculture, about 92% in one settlement category): "distinguishable from chance, not from confound". Terrain ruggedness is a clean null. Carneiro's circumscription is not tested. |
| 8d | EA034 high gods, "active but not supporting morality" (40 societies) | Exploratory: no predicted result, no floor. Mostly a **two-lineage story**: Atlantic-Congo is 15 of the 40 and environmentally tight (tighter than every random draw of that size); a small Nilotic set (4) likewise; three Sino-Tibetan societies are related but not environmentally coherent. Three **unrelated** Arctic Siberian peoples (Chukchi, Yakut, Yurak-Samoyed) form the tightest sub-group in the set. About **14 societies are explained by neither ancestry, climate nor proximity** (the "singleton residual"). |

A sanity anchor in 8d: placing the Hopi in the same climate space, two of their ten nearest non-family neighbours are Hano and Navajo, both documented cases of cross-language contact in the same place, with no contact information fed in.

A separate worked-example track (docsv4, WO2 and WO3, early August 2026) tested whether environmental discrimination of a trait **attenuates with causal distance from material constraint** (tiers: subsistence, settlement, social organisation, cosmology), with a continent-controlled variance decomposition. By my 10 Aug session log the prediction was **falsified**: high gods (the most distant tier) kept a within-continent omega-squared of 0.267, larger than its marginal 0.110, even after continent (itself about 0.5 on temperature and seasonality) was held fixed. I have not re-read that notebook; it should be checked before any number is quoted.

## 4. What the records say the panel and the analysis cannot claim

- **Association, not mechanism.** Environment as constraint, not determinant (8a); high-level traits route through subsistence (8b, 8c).
- **Family control is shallow ancestry.** Language family reaches back a few thousand years; "unexplained by environment and family" is not "unexplained by everything" (deep descent and undocumented contact remain). As far as the records show, areal contact between unrelated families is looked at descriptively (the Siberian trio, Hano and Navajo, the Isolates view) and not removed by a separate control.
- **Sampling.** D-PLACE is unevenly sampled, so some societies rank as isolated because their region is thinly covered. 13% of societies have no basin and are excluded, and they are mostly islands and coasts.
- **Container caveat.** A society is a point; its signature is that of the containing basin. About 13.4% show a gap of more than 2 degrees C between basin and site at Level 08; disclosed, not corrected.
- **Atlas variables carry no coding for missionization or religious contact**, so that check is unavailable for high gods.
- **Collinearity makes "net of" results thin.** With 92% of states in one subsistence category, the residual is an estimate on almost no independent variation. Effect size, not p-value, is the reading at n of about 900.
- **The page shows no test.** The findings above are not on the panel. The 28 Jul 2026 note records that the panel and the WO8 results never intersected by design, and that surfacing them is an open design decision.

## 5. Possible angles for a conference paper (CC's reading, for Opus to judge)

1. **A method paper.** A phylogenetically controlled environment and culture correspondence workflow with a stated reporting stance (report the confound share and effect size, never a "small real" residual), validated by a prediction that came true (the named axis deflated under the family control, another held) and by an unplanned contact check (Hopi). The records call this the strongest short-form story because it is defensible without any anthropology.
2. **An interface and design paper.** The hook versus no-hook asymmetry (confirmatory against exploratory displays), the rule that statistical language stays off the interface, family as a labelled layer, and the Isolates view as an instrument that refuses to give a verdict.
3. **A research question.** The unexplained singleton residual and the cross-family Siberian convergence, framed as targets for domain experts (Ruth is named as the follow-up for the Siberian case).

Gaps a reviewer would find: only three tests run (EA030, EA033, EA034) plus the calibration; findings sit in notebooks, not in a reproducible paper pipeline; the panel does not display the controls; how well the basin signatures match the ethnographic present (WO8a checked each predictor as "pre-1500 valid" or "full-record", but a reviewer will still ask); no handling of geographic spatial autocorrelation beyond family; D-PLACE coverage.

## Sources

`docs/cdop/pilot/` (`CDOP_PILOT_tracker.md` WO8 section; `wo8a` to `wo8d` `_exec_summary.md` and `_findings.md`; `note_societies-tab-vs-wo8.md`); `docs/cdop/citykin/` (`wo4_findings.md`, `note_to_opus_societies-dataviz.md`); `logs/2026_08/session_log_20260810.md`; `docs/edop/docsv4/` (`wo2_causal-distance.md`, `wo3_env-discrimination.md`, `wo4_EA045 -viz-change.md`, `wo5_findings.md`); `docsite/workbench/overview.md`; `app/templates/workbench.html`, `app/templates/_help_religion_isolates.html`, `app/db/societies_scan.py`, `scripts/cdop/distance_core.py`, `scripts/cdop/dbperm.py`.
