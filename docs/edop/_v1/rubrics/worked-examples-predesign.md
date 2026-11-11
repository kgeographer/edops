# Worked examples: pre-design notes

Draft of 2026-11-11. A log of thinking to revisit when worked-example work begins in January. Data work (GEDA, then LBDA) proceeds in the meantime.

## What the worked examples show

People who study the environmental side of a place's history work with whatever evidence exists for the period, from whatever source. Some periods have time-specific data, many do not. For the rest they reason from present-day conditions, on the ground that some features of a place change slowly or not at all, and they infer what they can.

The worked examples show that practice, and how EDOPS supports it. EDOPS assembles what is available for a place: time-specific data for the periods it covers, and the modern signature for the rest, organized in bands by persistence. The analyst decides what the evidence supports.

The examples state the limits of the evidence plainly. A gap in coverage is a fact about the available evidence, and the example names it at the outset.

## Method: sort premises by persistence

For a given historical argument:

1. List its environmental premises.
2. Tag each with the band it depends on and that band's persistence.
3. For each premise, say what the evidence supports:
   - **High persistence** (relief, river network, soils, broad biome boundaries): modern data supports the premise for early periods with little qualification.
   - **Moderate persistence** (climate means and variability): time-specific data where it exists; modern data as a baseline otherwise, stated as such.
   - **Low persistence** (land cover, modified hydrology): modern data describes the present only; time-specific sources (e.g. HYDE) where available; otherwise the premise remains an inference.

Persistence is itself a claim. Where the example relies on it, it says so and gives the grounds.

## Coverage rule for Band T

- LMR from 700 CE, everywhere. The 700 CE floor follows statements by the LMR authors on proxy coverage. *To confirm: exact source and wording, so the example can cite the authors directly.*
- Regional atlases from wherever each begins, within its footprint.
- Before 700 CE: the modern signature, plus HYDE land use where served.

## Example 1: Ukraine

**Source of the question.** Timothy Snyder's lectures on Ukraine's place in world history (video in hand).

**Evidence by period.**

| Period | Time-specific data | Otherwise |
| --- | --- | --- |
| Before 700 CE (Scythian, Greek colonies, Goths, Huns, Khazars, Slavic settlement) | None for climate; HYDE land use | Modern signature, by persistence |
| 700–1000 CE (to early Rus) | LMR (2°, annual, reanalysis) | Modern signature |
| 1000 CE on | LMR; GEDA summer scPDSI (0.5°, aggregated to basins) | Modern signature |

**Data notes.**
- GEDA (Great Eurasian Drought Atlas): 1000–2020 CE; tree-ring values 1000–1989, instrumental 1990–2020. Supersedes OWDA, ERDA and MADA. Zenodo, DOI 10.5281/zenodo.11059894, CC BY 4.0.
- OWDA was considered for 700–1000 and set aside: it has no values for Ukraine before about 700, covers only the north from 700 to 1000, and those values rest on very few, distant chronologies.
- GEDA skill for Ukraine, 1000–1400, still to check (paper supplement Fig. 3; per-point skill in the file if present).

**Likely high-persistence premises** (to test against the lecture): rivers draining to the Black Sea; steppe corridor and steppe/forest-steppe divide; chernozem soils.

**Low-persistence cautions:** Dnipro reservoirs, drained wetlands, ploughed steppe. The modern signature reflects these.

**Why Ukraine works as an example.** It exercises all three situations: no time-specific climate data, coarse data, regional data.

## Example 2: Southwest US (Chaco to the Rio Grande)

- LBDA (Living Blended Drought Atlas): JJA PMDI, 0.5°, 0–2005 CE. Covers Chaco's span (c. 850–1150) and the Rio Grande period in full.
- PMDI is a different index from GEDA's scPDSI. Values are reported per atlas and never combined across atlases.
- Shows the opposite situation to Ukraine: dense, period-matched evidence.

The two examples together show the range a user will meet. That is the case for doing both if hours allow.

## Connections

- **Rubric** (contract line, parameter selection by use case): the question "what can be said, on what grounds, from which band" is a first case of it. Write it up from the Ukraine example.
- **Presentation**: open each example with a short statement of what it demonstrates, including where evidence is absent.

## Next steps

- List Snyder's environmental premises from the lecture; tag each by band and persistence.
- Confirm the LMR 700 CE source.
- Check GEDA skill for Ukraine, 1000–1400.
- Revise *Regional dataset candidates for EDOPS* and the v1 plan: GEDA first, LBDA second; OWDA and ERDA as background.
- 