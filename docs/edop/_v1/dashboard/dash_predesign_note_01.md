# Dashboard pre-design note 01

Draft of 14 Nov 2026, by Fable from the first session with Karl. Options and questions, with the session's working direction recorded. Material to carve from. Hour figures are my guesses for CC to correct.

## 1. Working direction from the session

Stated or agreed by Karl on 14 Nov. Working assumptions, open to change.

- **Entry.** The splash page is the primary entry and part of the redesign. It says what EDOPS is and what a visitor can do, so that they click something to begin. Most v1 visitors will be new.
- **Lead message.** EDOPS generates environmental signatures for any place. See one for a settlement or polity: a description to read as prose, with the full signature underneath. Second message: signatures can be used in research; here are worked examples.
- **Three pages under the splash.** The Dashboard (the Sandbox reshaped and renamed), a signatures-in-use page (the Workbench reshaped), and the Data Explorer (intact, GEDA to be added).
- **Signatures in use.** Four tabs: Societies and African Regions (existing), Ukraine and Pueblo (new). WH Cities and Ecoregions stay live and leave the navigation for v1.
- **No rule-written interpretation of time-varying values.** Time is shown, not narrated.
- **Two layers of prose.** The stored summary covers bands A to E. Band T stays out of it, so adding a temporal source never forces regeneration.
- **Sources are shown, not selected.** Switching sources off goes to the roadmap file delivered with v1.
- **Long spans need a caution** at the year inputs.
- **dash_wo01** (the summary at Level 08) is with CC.

Proposed and not yet confirmed:

- **Naming.** "Signature" for the data, "summary" for the prose now called the profile. The splash currently uses "profiles" and "signatures" as synonyms.
- **Use scenarios** (section 2).

## 2. Use scenarios

Proposed as drivers of features. Karl liked the general framing; each row still needs a yes, no or amendment.

| # | Who | What they do | What it asks of the site | Proposed weight |
| --- | --- | --- | --- | --- |
| 1 | Newcomer, from the splash or a link on a WHG place page | Looks up one place they know and reads about it | Summary first; a result without parameter choices; a permalink | Driver |
| 2 | Historian with a place and a period | Wants what is known for those years | Band T readable, GEDA shown; a statement of which sources apply | Driver |
| 3 | Researcher building an argument | Follows a worked example, then tries the reasoning on their own place | The in-use page; Similarity, Context and the ring as they are | Served by the in-use page |
| 4 | Data user | Wants the numbers | A "data as JSON" link; the API docs | A link |
| 5 | Regional or polity scholar | Wants a polity or area at a date | The Polities tab as it is; no summary | Kept, not promoted |

## 3. Inventory of the Sandbox

From the cheat sheet (v0.4.2) and Karl's screenshots. The verdicts are proposals.

| Part | What it does | Proposal |
| --- | --- | --- |
| Splash, three cards | Names three tools; captions explain them | Changes: names what a visitor can do (section 4) |
| Settlements and Polities tabs | Two ways in; switching resets the other | Stays |
| Place lookup, identifier, lat/lon | Resolves to one point via WHG | Stays; may become the splash's first action |
| Load an example | Sets scope, level, Band T and years; does not run | Stays; in shapes B and C it runs |
| Scope: single basin | The containing basin | Stays, the default |
| Scope: basin ring | Centre basin plus neighbours to compare one at a time | Stays |
| Scope: buffer | Distribution over basins in a radius | Open: Karl has doubted it (cheat sheet 7.2 item 12); WO-02 holds the evidence |
| Level 06 / 08 | Basin scale | Stays; its effect on the summary waits on dash_wo01 |
| Band checkboxes A to E, T | Filter rows; T reveals years | Stays; letters mean nothing to a newcomer, so needs a plainer face or a place under "options" |
| Band T years | Free entry, -10000 to 2025 | Stays; gains the long-span caution |
| Get signature | Runs the query | Stays; its role differs by shape (section 5) |
| Render variable | Paints basins by one variable | Stays |
| Map tab | Basin, rivers, scope preview, polity slices | Stays |
| Signature tab | Band accordions; Band T opens first | Changes: no longer the first view; gains the sources statement and the GEDA block |
| Analysis | Basin context, local and upstream, water provenance | Stays; linked from the summary's Water section |
| Seasonality | Climate diagrams and a generated sentence | Stays; linked from Climate |
| Context | Global and regional percentiles, map, generated paragraph | Stays; linked from Surroundings |
| Similarity | Lens-based matching basins | Stays |
| Atlas | Global precipitation regime map, not tied to a place | Karl's earlier decision: carried as an option, tab or alternate screen. Where is open |
| Left-column intro text | Explains signatures | Changes: most of it moves to the splash |

### What each control does to results today

This is the staleness picture a reshaped panel has to make consistent.

| Control | Effect on results on screen |
| --- | --- |
| Scope, buffer radius | Clears the results |
| Level | Redraws the map and choropleth; refreshes Context and Similarity if open; the Signature tab is left as it was |
| Band checkboxes, Band T years | No effect until Get signature (my inference; the cheat sheet does not say) |
| Ring member | Replaces Signature, Analysis, Seasonality, Context and Similarity with that basin's |
| Polity slice | Map and choropleth update; the Signature tab waits for Get signature |
| Context radius, Similarity lens and thresholds | Re-run that tab only |
| Settlements / Polities | Hard reset of the other |
| Reset | Clears everything |

## 4. Elements common to every shape

**Splash.** In words:

- What this is: two or three sentences.
- See a place: one action (type a place or pick an example) that lands in the Dashboard.
- See signatures in use: the worked examples, across many places (Societies, African Regions) and one place through time (Ukraine, Pueblo).
- The data underneath: Data Explorer, documentation, API, smaller.

**Summary.** The stored profile text for the place's basin, headed "Containing basin for {place}" as Analysis, Seasonality, Context and Similarity already are. It says in a line that it does not describe the years entered. Its sections link to the tabs that back them. It is silent for buffers and polities.

**Band T.** The existing panels, plus a GEDA block of the same type beside LMR (decided earlier), headed by a sources statement: fixed sentences with slots, read from the `sources` block, saying which sources apply to this place and span and which do not, with reasons.

**Signatures-in-use page.** Each tab gets a short block: the question, what the signature contributes, what was found. Tooltips for terms; the docs for the full write-up. Societies and African Regions need this prose and some redesign to read as examples. An optional "Show me" guide is possible: steps that set the page to a state and say what to notice. The Ukraine and Pueblo tabs could use the same mechanism.

**Permalink.** A URL that opens a place in the Dashboard (already parked in the v1 plan). It serves the WHG link, the splash's first action and any guide.

| Element | Needs from the payload or back end | Rough hours |
| --- | --- | --- |
| Splash | Nothing | 6 to 10, mostly prose |
| Summary shown in the Dashboard | Stored profile fetched by point; how point units are served (dash_wo01 item 2) | 20 to 30 (the v1 plan's figure) |
| Sources statement | `sources` block, already in every response; the list of its states (later work order) | 6 to 10 |
| GEDA block | Rows already returned; display only | 10 to 15 |
| Long-span caution | A length from measured payload sizes | 2 to 4 |
| In-use page: rename, navigation, intro blocks for two tabs | Nothing | 8 to 15, plus Karl's prose |
| Ukraine tab, Pueblo tab | Per the worked-example work in January; Pueblo is stronger with LBDA | 25 to 35 each (the v1 plan's figure) |
| Permalink | URL parameters read on load | 5 to 10 |
| "Show me" guides | Each panel settable to a named state | Not estimated |

## 5. Three shapes for the Dashboard page

They differ in when the first result appears and how much of the left panel is rebuilt.

### Shape A: summary as a tab

The current order kept. Place, parameters, Get signature; the result opens on a new Summary tab instead of Band T.

```
[ place ] [ scope level bands years ] [Get signature]
-----------------------------------------------------
Map | Summary* | Signature | Analysis | Seasonality | Context | Similarity
```

- First view: the map, as now. Prose appears after Get signature.
- Cost beyond the common elements: little.
- Weakness: a newcomer still meets Level and band letters before seeing anything.

### Shape B: summary on pick

Choosing a place shows its stored summary and the map at once. Get signature stays as the deliberate step for the full signature with chosen parameters.

```
[ place ]  ->  Map + Summary (stored, Level 06 basin)
[ scope level bands years ] [Get signature]  ->  Signature and the other tabs
```

- First view: prose and map, with no parameter choice.
- Cost beyond the common elements: about 5 to 10 hours.
- Weakness: summary and signature are two moments; the summary assumes single basin and Level 06 until dash_wo01 says otherwise.

### Shape C: configurator

Choosing a place runs the default query (single basin, Level 06, bands A to E). Scope, level, bands and years sit beside the result as adjustments; each re-runs or marks the result out of date. Years apply on an explicit step.

```
[ place ]  ->  Summary + Signature + tabs, all at defaults
[ scope | level | bands | years (apply) ]  adjust what is on screen
```

- First view: the whole result at defaults.
- Cost beyond the common elements: about 25 to 40 hours; the left panel is rebuilt and every control needs one consistent behaviour (the table in section 3).
- Weakness: the largest change; polities need a default slice; time becomes something added after the place.

## 6. Questions for Karl

1. **Entry order:** shape A, B or C?
2. **Use scenarios:** which rows of section 2 stand?
3. **Naming:** "summary" for the prose and "signature" for the data, on the splash and throughout?
4. **Summary at Level 08:** which of the four behaviours? Waits on dash_wo01.
5. **Where the summary sits:** its own tab, or above the tabs and always visible?
6. **Buffer scope:** keep, demote or retire?
7. **Polities:** equal billing with Settlements, or second?
8. **Band T headline value:** mean, sum or distribution first? A notebook figure could show the alternatives.
9. **Ukraine and Pueblo tabs:** a step-through with live panels, or prose with figures? Suggested for January.
10. **"Show me" guides:** worth the state-setting work, or exploration only?
11. **Atlas:** where does it live?

## 7. Parked for the roadmap file

- Switching sources on and off.
- Rule-written or LLM-written prose about time-varying values.
- Summaries for sets of basins (buffers, polities).
- Storing Level 08 profiles, unless dash_wo01 makes it cheap.

## 8. Work orders and loose items

- **dash_wo01**, issued: the summary at Level 08.
- **A later work order on time:** payload size and response time against span length; every state of the `sources` block over a sample; which route the Dashboard's Band T comes from (the public basin route mixes methods, the engine path does not).
- **Loose:** what identifies a stored record's inputs, so stale records can be found; what state each panel can be set to from a URL today; the LMR cells under the Chaco and Santa Fe basins and their series for 850 to 1300.