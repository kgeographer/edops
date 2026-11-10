# WO-06 summary: comparing a place's basin with the basins around it

2026-11-07. Read this first; the detail is in `wo06_results.md`. The ten filled_profiles are in `wo06_filled_profiles.md`. Wording is in `profile_templates.md` (now Version 5).

## What was built

Six units now fill from real data: S2.3 (climate against the ring), S5.2 (land cover against the ring), S6.2 (flow relation), S6.3 ("all across its divides"), S6.4 (measures outside the neighbours' range) and S6.5 (what the basin is highest or lowest in). Each states only what is true without a cutoff: extremes, counts, "all of them". Where nothing true can be said the unit is silent. Rules are in `scripts/edop/whg/wo06_rings.py`; the neighbours' local values are fetched once and kept in `output/edop/whg/wo06_ring_values.csv` (315 basins), so rules can be tuned without re-fetching.

## Gate

- Ten filled_profiles regenerate from the live template (Version 5) with the six units filled where they apply and silent where not: met once Cell 4 is rerun against the live file (done on the target copy; the swap changed no wording).
- Firing rates over the 306 sample basins: reported below and in the results file.
- Housekeeping (I-3, R1, R2, E3): none done. Each blocker is named in the results; all four were parked by Karl until after WO-07.

## Firing rates (306 sample basins)

| Unit | Speaks | Silent |
|---|---|---|
| S2.3 | 278 | 28 |
| S5.2 | 232 | 74 |
| S6.2 | 298 | 8 |
| S6.3 | 70 | 236 |
| S6.4 | 208 | 98 |
| S6.5 | 144 | 162 |

28 basins have fewer than three neighbours, so every ring comparison stays silent for them (S6.2 still reports counts).

## Things to know

1. **The ring sentences speak for almost everyone.** Santa Fe gets five ring sentences (counting the flow sentence), as many as Timbuktu; Tbilisi, which the WO expected to be fuller, gets three. The WO's guess about Santa Fe did not hold. The count form ("more than four of the five") is nearly always available.
2. **Extremes depend on the ring.** With 3 to 4 neighbours about 43% of basins are an extreme in S2.3; with 7 to 8, 4%. A core that is the smallest of its ring has an extreme 92% of the time, the largest 50%. "The least precipitation of four basins" is true but weak.
3. **S6.4 changed during the WO.** The first version ("within the range on 23 of 23 measures") said nothing for large basins; it now counts the measures outside the range and is silent when there are none. Where it speaks the median is 3 of about 22; 46 basins are outside on only one measure, which is thin because the sentence does not say which. No floor was set (Karl's call); logged as an open question.
4. **Precipitation wording.** "Driest" and "wettest" were dropped for precipitation: it now "receives the least/more precipitation"; "arid" and "humid" are used for aridity only. The Water section's `S3.2b.wetter` has the same issue and was left (WO-05 wording).
5. **Findings for the endpoint.** The ring payload carries no mean elevation and no forest share; both were read from `public.basin06`. Wetland is excluded from S6.5 because the catalog defines no wetland groups.

## For Karl or Opus to decide

- S6.4 floor (say, at least three measures) or naming the measures.
- Whether count sentences should speak at all, or only extremes and "all" cases (changes Santa Fe's five to about two); best decided after Ruth and Stephen have seen a sample.
- Raising the neighbour minimum for extremes only (small rings).
- Number words run to ten ("ten of the 12" mixes forms).
- The four housekeeping items, after WO-07.
