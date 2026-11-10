"""WO-02 Step 3, family 8: Cross-band (which variables sit furthest from the global median, and how typical a place is overall).

An item is a band (XB-01) or the whole query (XB-02 to XB-04). The distance is |percentile - 50|, in percentile points, over
rows with a usable percentile (status ok, a score, not suppressed). Zero-aware variables are left out: their percentile 0 means
'zero here' and their other values rank only the non-zero basins, so their distance from the median is not comparable
with a global rank. So is a variable with no zero fraction in the catalog (reservoir_vol: 77% of basins score exactly 0 on it,
all tied at percentile 0, so it would be the furthest from the median in most queries). Rules describe distances and never judge them (WO constraint 1).
"""
import statistics
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import ordinal, ZERO_AWARE_THRESHOLD
from scripts.edop.dashboard import wo02_rules_localup as LU

CONT = ("area_weighted", "distribution_only", "dominant_basin")
BAND_NAME = {"A": "Band A (physiographic)", "B": "Band B (hydro-climatic)", "C": "Band C (bioclimatic)",
             "D": "Band D (anthropocene markers)", "E": "Band E (coastality)"}
TOP_BAND, TOP_ALL = 2, 3          # how many variables each sentence names (a display choice)
MIN_BAND, MIN_ALL = 3, 5          # fewest eligible variables for a band or an overall sentence
TAIL = 10                         # XB-03 counts variables at or below this percentile or at or above 100 minus it; swept in the notebook

STATEMENTS = [
    dict(id="XB-01", name="Furthest from the global median, within a band",
         inputs="representative_score of the band's rows with a usable percentile; catalog zero_fraction (zero-aware rows, and rows with no zero fraction, excluded)",
         rule="Band with at least three eligible rows: name the two variables whose percentile is furthest from 50, with their percentiles. A local variable and its upstream version count as one (the one further from the median is named, carrying its '(upstream)' label).",
         applies_to="single basin, buffer, polity; Bands A to D (Band E has too few eligible variables); L6, L8",
         does_not_apply_when="fewer than three eligible variables in the band; rows empty, suppressed or zero-aware are not counted",
         template="{band}: the variables furthest from the global median are {name} ({ord} percentile) and {name} ({ord}).",
         in_ui_today="no: the Sandbox lists rows by band without ranking them by distance from the median",
         needs_new_data="catalog zero fractions (not in the payload); the catalog has none for reservoir_vol, which is mostly zero (77% of basins score exactly 0), so it is excluded"),
    dict(id="XB-02", name="Furthest from the global median, across all bands",
         inputs="as XB-01, over all bands",
         rule="At least five eligible variables: name the three whose percentile is furthest from 50, a local and its upstream version counting as one.",
         applies_to="single basin, buffer, polity; L6, L8",
         does_not_apply_when="fewer than five eligible variables",
         template="Across all bands, the variables furthest from the global median are {name} ({ord}), {name} ({ord}) and {name} ({ord}).",
         in_ui_today="no",
         needs_new_data="no"),
    dict(id="XB-03", name="How many variables lie in the lowest or highest tenth",
         inputs="percentiles of the eligible rows",
         rule="At least five eligible variables: state how many are at or below the 10th percentile or at or above the 90th (the tails). The 10 is a defined tenth, not a judgement; the notebook reports a grid of tail widths.",
         applies_to="single basin, buffer, polity; L6, L8",
         does_not_apply_when="fewer than five eligible variables",
         template="{k} of the {m} variables with a global percentile are at or below the 10th percentile or at or above the 90th.",
         in_ui_today="no",
         needs_new_data="no"),
    dict(id="XB-04", name="How far the place is from the global median overall",
         inputs="percentiles of the eligible rows",
         rule="At least five eligible variables: state the median distance of the variables' percentiles from 50, in percentile points (0 is at the median, 50 is at an extreme). For an area add that averages over many basins sit closer to the median than a single basin's values (about 25 typically), because the scale depends on scope.",
         applies_to="single basin, buffer, polity; L6, L8",
         does_not_apply_when="fewer than five eligible variables",
         template="Across the {m} variables with a global percentile, the median distance from the global median is {d} percentile points. | ...; averages over many basins sit closer to the median than a single basin's values, which are typically about 25.",
         in_ui_today="no",
         needs_new_data="no"),
]


def _pair_key(variable, level):
    """The local variable's name for a local or upstream variable, so a pair is one variable."""
    for local, up in LU.partners(level).items():
        if variable in (local, up):
            return local
    return variable


def _dedupe(vals):
    """One entry per local-and-upstream pair: the one furthest from the median (ties: by name)."""
    best = {}
    for v in vals:
        k = v[3]
        if k not in best or (-abs(v[2] - 50), v[0]) < (-abs(best[k][2] - 50), best[k][0]):
            best[k] = v
    return sorted(best.values(), key=lambda v: (-abs(v[2] - 50), v[0]))


def eligible(ctx, row):
    """(variable name, band, percentile, pair key) for a row with a usable global percentile, else None."""
    if row["method"] not in CONT or row["status"] != "ok" or row.get("score_suppressed") or row.get("representative_score") is None:
        return None
    if row["method"] != "dominant_basin":
        zf = P.zero_fraction(row["variable"], ctx["level"])
        if zf is None or zf >= ZERO_AWARE_THRESHOLD:       # unknown zero fraction (reservoir_vol) is excluded, not assumed global
            return None
    return (row.get("friendly_name") or row["variable"], row["band"], row["representative_score"], _pair_key(row["variable"], ctx["level"]))


def eligible_rows(q):
    pairs = P.ae_rows(q)
    return [(e, ctx) for ctx, r in pairs for e in [eligible(ctx, r)] if e is not None], (pairs[0][0] if pairs else None)


def evaluate_query(q):
    el, ctx0 = eligible_rows(q)
    out = []
    if ctx0 is None:
        return out
    base = dict(qid=ctx0["qid"], scope=ctx0["scope"], level=ctx0["level"], n_units=ctx0["n_units"], method=None, status=None)

    def rec(i, item, applies, reason=None, text=None, stat=None):
        out.append(dict(base, id=i, variable=item, applies=applies, reason=reason, text=text, stat=stat))

    vals = [e for e, _ in el]
    for b in "ABCDE":
        vb_all = [v for v in vals if v[1] == b]
        if len(vb_all) < MIN_BAND:
            rec("XB-01", f"band {b}", False, "fewer_than_3")
        else:
            top = _dedupe(vb_all)[:TOP_BAND]
            rec("XB-01", f"band {b}", True,
                text=f"{BAND_NAME[b]}: the variables furthest from the global median are " + " and ".join(f"{v[0]} ({ordinal(v[2])} percentile)" for v in top) + ".",
                stat=abs(top[0][2] - 50))
    allv = sorted(vals, key=lambda v: (-abs(v[2] - 50), v[0]))      # every eligible row: counts and medians
    m = len(allv)
    if m < MIN_ALL:
        for i in ("XB-02", "XB-03", "XB-04"):
            rec(i, "(all bands)", False, "fewer_than_5")
    else:
        top = _dedupe(vals)[:TOP_ALL]                                   # a local and its upstream version are named once
        rec("XB-02", "(all bands)", True,
            text="Across all bands, the variables furthest from the global median are " + ", ".join(f"{v[0]} ({ordinal(v[2])})" for v in top[:-1]) + f" and {top[-1][0]} ({ordinal(top[-1][2])}).",
            stat=abs(top[0][2] - 50))
        k = sum(1 for v in allv if v[2] <= TAIL or v[2] >= 100 - TAIL)
        rec("XB-03", "(all bands)", True, text=f"{k} of the {m} variables with a global percentile are at or below the {ordinal(TAIL)} percentile or at or above the {ordinal(100 - TAIL)}.",
            stat=k / m)
        d = statistics.median(abs(v[2] - 50) for v in allv)
        t = f"Across the {m} variables with a global percentile, the median distance from the global median is {d:.0f} percentile points"
        t += "." if ctx0["n_units"] == 1 else "; averages over many basins sit closer to the median than a single basin's values, which are typically about 25."
        rec("XB-04", "(all bands)", True, text=t, stat=d)
    return out


def counts(queries):
    """Eligible and excluded rows over single-basin and buffer queries: for the notebook's checks."""
    import collections
    c = collections.Counter()
    for q in queries:
        for ctx, r in P.ae_rows(q):
            if r["method"] not in CONT or r["status"] != "ok" or r.get("score_suppressed") or r.get("representative_score") is None:
                continue
            if r["method"] == "dominant_basin":
                c[(r["band"], "eligible")] += 1
                continue
            zf = P.zero_fraction(r["variable"], ctx["level"])
            c[(r["band"], "no zero fraction (excluded)" if zf is None else "zero-aware (excluded)" if zf >= ZERO_AWARE_THRESHOLD else "eligible")] += 1
    return c


def tail_share(queries, tails=(5, 10, 15, 20, 25)):
    """Per query: share of eligible variables in the lowest or highest `tail` points, for each width."""
    out = []
    for q in queries:
        el, ctx0 = eligible_rows(q)
        vals = [e[2] for e, _ in el]
        if len(vals) >= MIN_ALL:
            out.append((q["id"], {t: sum(1 for v in vals if v <= t or v >= 100 - t) / len(vals) for t in tails}))
    return out


def leader_frequency(queries, weights):
    """Weighted share of queries in which each variable is the one furthest from the global median (XB-02's first name).
    Pass the queries of one kind (single L6, buffer L6 or single L8) so the weights sum to 1."""
    import collections
    cnt, tot = collections.Counter(), 0.0
    for q in queries:
        el, _ = eligible_rows(q)
        vals = [e for e, _ in el]
        if len(vals) < MIN_ALL:
            continue
        lead = sorted(vals, key=lambda v: (-abs(v[2] - 50), v[0]))[0]
        cnt[lead[0]] += weights[q["id"]]
        tot += weights[q["id"]]
    return {k: v / tot for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])}


def zero_aware_level_difference():
    """Variables whose zero-aware status (catalog zero fraction >= 0.20) differs between L6 and L8: (variable, L6 fraction, L8 fraction)."""
    c6, c8 = P.catalog(6), P.catalog(8)
    out = []
    for v in c6.index:
        if v in c8.index:
            z6, z8 = P.zero_fraction(v, 6), P.zero_fraction(v, 8)
            if (z6 is not None and z6 >= ZERO_AWARE_THRESHOLD) != (z8 is not None and z8 >= ZERO_AWARE_THRESHOLD):
                out.append((v, z6, z8))
    return out
