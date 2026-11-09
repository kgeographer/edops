# WO-09 summary

9 Nov 2026. Detail and evidence: `wo09_results.md`. Profiles from the current template (v19): `wo09_filled_profiles.md` (nine places with a basin, and Tristan da Cunha). Branch `whg-profile`, nothing pushed.

## What was done

- **Items 1 to 10 of the WO, all done.** The ring table now gives flagged shares their value (patched from `basin06`, not rebuilt: 13,617 rows, 1,346 of them really 1%); only Timbuktu's comparison sentence changed. "None" is said only of a true zero (292 "no ..." statements over 306 basins; none has a raw value above zero). Zero-share wording, the no-percentile list, the OSM credit, the point-source line and the Tristan da Cunha profile are in. S7.3 is silenced. The Wikipedia button is hidden where its link is flagged (Timbuktu).
- **Added: a OneEarth button** (template v18) on every profile, opening in a new tab. All 845 pages we hold slugs for answered 200. It gives Timbuktu a working ecoregion link in place of the hidden Wikipedia one.
- **Template v16 to v19**; tests: 619 passed, 21 skipped.

## Where we stand: placeholders remaining

Still **4 of the 22** at the WO-04c baseline; nothing changed in the count in this WO. 16 are filled and 2 were tried and dropped (S1.3, S7.1a). The four:
- **S1.2b**, the one-line ecoregion gist: needs reliable summaries (see below).
- **S6.2c**, a description of a neighbouring basin: needs ring rules and wording.
- **S8.1b**, the years of the datasets: needs the glossary.
- **S9.1**, the link into EDOPS: needs the URL scheme from WHG.

## Ecoregion links: where this stands (E1, E2)

- The button problem is solved with OneEarth links. The Wikipedia links remain unreliable (129 of 847 flagged). Wikidata, matched by name, confirms 583 of ours, differs on 18, leaves 215 unmatched.
- **The gist (S1.2b) is blocked on One Earth's permission** to show their text; their terms reserve it. Karl is writing to them. If they decline, gists come from Wikipedia (CC BY-SA) once the links are settled, generated with the Claude API and marked as generated.

## Answers to the WO's questions

- **I-3** (the missing-value marker stored as a class): closed in practice. `missing.class_label` handles it and is tested; no live profile code builds such a class frame.
- **Timbuktu's "no cropland":** a true zero. **Flagged-link count:** one of the nine places with a basin loses the Wikipedia button (Timbuktu).
- **Fallbacks** were already in the fill notes.

## Decisions waiting for Karl

1. **Send the email to One Earth** (draft in `misc/oneearth_email_draft.txt`).
2. **Push.** `whg-profile` is local only, and no push until Karl says so. The WO says to push as a backup after the gate.
3. **Wikipedia work for the 18 differing and 215 unmatched ecoregions:** wait for One Earth's answer, or start now?

## Still parked

R1, E3, S3.2b ("wetter"), the Caspian wording (R3), world-scale river names, the coast-flag note to HydroSHEDS, monthly arrays in the `/whgmodal` payload (all in the open-items file).
