# Profile store: a design to react to

Draft of 15 Nov 2026, by Fable for Karl and CC. One page. It reasons from `dash_wo01_results.md`; I have not seen the generator's code, so every claim about what is cheap is for CC to confirm or correct.

## The rule

Never store finished profile text. Store facts per basin, one table per kind of fact and per source, and assemble the text when a place is asked about.

WO-01 already forces the second half: the Setting sentence mixes place and basin facts, and "also takes in parts of…" depends on the point, so text is assembled per place in any case.

## What is stored

Every table is keyed by level and `hybas_id`, and stamped with source version, script commit and build date.

| Table | Holds | Built by |
| --- | --- | --- |
| Basin facts | The values, global percentiles and classes the templates read (bands A to E) | One pass over the basin table per level; the percentile is a rank over all basins, so the database computes it for all of them together |
| Neighbours | Adjacent pairs, shared border, bearing | One spatial self-join per level |
| Flow | Which neighbours drain into the basin and which it drains into | One traversal of `next_down` per level |
| Ecoregion shares | Every ecoregion in the basin with its share | One intersection query per level, basin first (the form WO-01 found fast) |
| Per-source facts | Only if a profile is ever to say something fixed about a source (a coverage line, for example) | One pass per source |

Comparisons with neighbours (highest, lowest, "more than four of seven") can be stored as now, or derived at request time from basin facts joined to neighbours, which is a handful of rows per basin. CC to say which.

## What happens on request

1. Resolve the point to its basin at the level asked for.
2. Look up the point facts: elevation, the point's ecoregion, river distances.
3. Read the basin's rows from the tables.
4. Apply the rules, fill the templates, return the text and the template view.

Assembled text may be cached by point, level and template version. The cache is disposable.

## What a change costs

| Change | Rerun |
| --- | --- |
| Wording in `profile_templates.md` | Nothing; clear the cache |
| A rule that uses facts already stored | Nothing; clear the cache |
| A new fact from a source already in use | One column or table, one pass |
| A new source | That source's table only |
| A new version of one source | That source's table only |
| Level 08 | The same passes with level 8 |
| A new BasinATLAS | Everything (a platform migration in any case) |

So feedback from Pitt on the sample profiles, which will mostly concern wording and which sentences speak, costs no bulk run. The fact tables can be built before that feedback arrives.

## Expected cost of the build

WO-01's 1.6 s per basin is the cost of asking the running app for one signature at a time. The passes above do not use that path. I expect minutes to hours per level on one machine, to be measured at Level 06 first.

## Acceptance test

For the ten sample places, text assembled from the store at Level 06 is identical to the profiles stored today.

## Questions for CC

1. Does the engine already hold global percentiles for every basin (the cheat sheet mentions `compute_global_scores`), or can its ranking query be run once for all basins?
2. Which facts does the generator take from its two requests to the app, and can each be read from a table instead?
3. Neighbour comparisons: stored, or derived on request?
4. Point lookups: what do they cost per request, does any call leave the database (point elevation), and should results be cached by place?
5. Is anything in the generator procedural per basin in a way a set-wise pass cannot replace (the flow classification, for example)?
6. The index on `hybas_id` and the basin-first ecoregion query: add both, with the query checked for identical results on a wider sample than two basins.
7. Does this change anything the `/whgmodal` contract has already promised WHG?
8. 