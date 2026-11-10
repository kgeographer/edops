# WO-10a: adjustments to the sample profile page

2026-11-10, drafted by Opus after reading `wo10_summary.md`, `wo10_results.md`, `kaifeng.json` and the full-page screenshot of Kaifeng. Reviewed by Karl. Goal-setting, not a specification. Small items; the cover note waits until this is done.

## Goal

Settle the wording problems and the open questions A to E from WO-10, so the page at `/profiles` is ready to send to Stephen and Ruth. Branch `whg-profile-page`.

## 1. Wording (template v21)

Karl saves each change with a version bump and a Changes line.

**a. Land cover sentence (S5.1c).** The percentages can add up to more than 100% because two datasets share one sentence. Name the second dataset in the sentence instead of adding a note to About:

```
S5.1c: in the GLC2000 land cover map, the commonest class other than cultivated land is {label}, at about {share}%
```

Change the cover part of `S5.both_none` the same way: "in the GLC2000 land cover map, the commonest class is {label}, at about {share}%". Check the result at Chaco Canyon, Santa Fe and Poltava.

**b. Drop the "no percentile" sentence (S8.2) from the profile.** It explains an absence the page does not show, and uses catalog names. Silence at zero is already the rule elsewhere. Remove `{S8.2}` from `S8.frame` and `S8.frame.noyears`; keep the list in the stored record.

**c. The S9 frame stays as it is (Karl's decision).** The Wikipedia button shows where a valid link exists; ecoregion names already link to OneEarth inline. No change until One Earth replies about what we may do with their pages. Confirm in the summary which gate decides whether the Wikipedia button shows.

## 2. "Profile as JSON" should show the proposed response

The button now opens the generator's stored record (about 33 KB, with template segments, slot values and fill notes). Stephen will read it as what WHG would receive, which misleads on size and structure.

- Write a small transform from the stored record to the proposed `/whgmodal` response shape, and have the button open that, as ten static files.
- Shape (CC's proposal, agreed): place, basin id, template version and date; `sections[]` with `id`, `title`, `text` and `runs`; links as absolute URLs; credits as a field (the OSM/ODbL line wherever a river name appears); `monthly` (see 3). Template lines, slot values, unit traces and fill notes stay out; note in the summary that they would come with `?explain=1`.
- The internal record need not be linked from the page. The template view stays.
- Report the size of each file.

## 3. Monthly arrays (question B)

Always carried: 12 precipitation and 12 temperature values, with units and `scope: "basin"` and a short note that they describe the basin, not the point. Use the same values the chart draws.

## 4. Point and basin units (question C): no build, a note for the endpoint work

The plan for January: store the basin record; compute the point units at request time. Point ecoregion (polygon lookup), nearest river and the snap are local and fast. Only elevation needs an outside call. Two routes to record in the summary: WHG sends its own elevation with the request, since its place pages already show one; or a local elevation grid (open item L1). Nothing to build now.

## 5. Permalink (question D): a note

A permalink into the Sandbox is the EDOPS half of S9.1: EDOPS defines the URL, WHG builds it from a place's name and coordinates. So S9.1 is not blocked on WHG. Move it from "needs URL scheme from WHG" to January work on our side in the open-items file and the v1 plan. Nothing to build now.

## 6. Small fixes seen on the Kaifeng page

**a. "Its water flows on through two of them."** Accurate since WO-07, but a reader will wonder how water flows through two basins. Report the cause in one line. If it is one basin downstream and a second beyond it, propose wording such as "It drains into one of them, and its water then passes through a second." Karl saves the wording.

**b. Chart axis ticks.** The precipitation axis shows 99 and 198, half and all of the maximum. Use round ticks (for example 0, 100, 200) on both axes.

**c. Sources line.** It lists Wikipedia, which appears only as a button where a link has passed the check. Karl may reword; no action unless he does.

## Provisos

- Wording through `profile_templates.md` as its header says; rules and page code as before.
- Regenerate all ten records; edge cases first (Tristan da Cunha, Alexandria, Utqiagvik, Kaifeng).
- No push, no deploy, no merge.

## Deliverables and gate

- `wo10a_summary.md`: one page, read first.
- A new full-page screenshot of one place (Chaco Canyon, which shows the land cover change).
- One file of the new response shape (Kaifeng), for Opus.

**Gate:** the ten records regenerate from v21; the land cover sentence names the GLC2000 map; S8.2 is gone from the page; "Profile as JSON" opens the response shape with monthly arrays; the Kaifeng flow sentence is explained; the chart ticks are round.
