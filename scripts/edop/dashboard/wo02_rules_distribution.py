"""WO-02 Step 3, family 5: Distribution (how the member basins' values are spread behind a headline percentile).

Rules read the detail block of a multi-basin, continuous row with status ok and a score (core window, core share, p10 to p90,
min to max) and the coherence label. Each states a number and never judges (WO constraint 1). The coherence label rests on
the engine's provisional cutoff (core share 0.65); the notebook sweeps a grid on the core share, and the label is not used
where it flips.
"""
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import ordinal

CONT = ("area_weighted", "distribution_only")
MIN_COHERENT = 5          # the engine clears the coherence label below this many basins (engine._MIN_COHERENT_BASINS)

STATEMENTS = [
    dict(id="DIS-01", name="Core window and core share",
         inputs="detail.core_share, window_lo, window_hi; n_units; score_suppressed",
         rule="Five or more basins, continuous variable, status ok, score present: state the share of the area that lies inside the densest window and the window's bounds.",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="fewer than 5 basins (DIS-05); one basin; score suppressed (EMP-06); status not ok",
         template="{name}: {share} of the area lies between the {ord} and {ord} percentiles.",
         in_ui_today="partly: the histogram shows a pale +/-15 point core window; the core share is not shown",
         needs_new_data="no"),
    dict(id="DIS-02", name="Middle 80% of the area (p10 to p90)",
         inputs="detail.p10, detail.p90; n_units",
         rule="Five or more basins, continuous variable, status ok, score present: state the p10 and p90 percentiles. By definition 80% of the area (by weight) lies between them.",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="fewer than 5 basins (DIS-05); one basin; score suppressed; status not ok",
         template="{name}: the middle 80% of the area (by weight) lies between the {ord} and {ord} percentiles.",
         in_ui_today="partly: distribution_only rows show a p10 to p90 range bar; area_weighted rows show min and max (cheat sheet 4.2)",
         needs_new_data="no"),
    dict(id="DIS-03", name="Lowest and highest basin",
         inputs="detail.distribution.min and max; n_units",
         rule="Several basins, area_weighted row with status ok: state the lowest and highest member-basin percentile.",
         applies_to="buffer, polity; area_weighted; L6, L8",
         does_not_apply_when="one basin; distribution_only rows (no distribution block); status not ok; score suppressed",
         template="{name}: across the {n} basins, values run from the {ord} to the {ord} percentile.",
         in_ui_today="yes: the histogram's two axis ends are labelled with the minimum and maximum (cheat sheet 4.2)",
         needs_new_data="no"),
    dict(id="DIS-04", name="Split: one value carries much of the area, a separate group lies elsewhere",
         inputs="coherence = split, representative_score, detail.core_share, window_lo, window_hi",
         rule="Five or more basins, coherence split (the engine's rule: one tied score holds at least half of the weight and at least 10% lies outside the core window): say the tie lies inside the core window and state the share of the area outside it; the headline is the mean over both, not the tied value (checked: it lies about 16 points from both p10 and p90 at the median).",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="coherence not split; fewer than 5 basins; score suppressed; status not ok",
         template="{name}: at least half of the area is tied at one value inside the {ord} to {ord} percentile window, and {share} of the area lies outside it; the headline, the {ord} percentile, is the mean over both.",
         in_ui_today="partly: a blue 'split' badge; the tied value and the share outside the window are not shown",
         needs_new_data="the tied value and its weight are not in the payload; the 'at least half' is the engine's rule; the tie lying inside the core window follows from that rule and is not checked row by row"),
    dict(id="DIS-05", name="Too few basins for a spread statement",
         inputs="n_units (2 to 4), coherence = null",
         rule="Two to four basins, continuous variable, status ok, score present: state the count and that no spread label is given because it needs at least 5; the lowest and highest values (DIS-03) are the whole distribution.",
         applies_to="buffer; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="five or more basins; one basin; score suppressed; status not ok",
         template="{name}: this {area} has only {n} basins, so no spread label is given (it needs at least 5).",
         in_ui_today="no: the Sandbox shows no badge for fewer than 5 basins and says nothing about why",
         needs_new_data="no"),
    dict(id="DIS-06", name="Coherence label (concentrated or spread) as wording",
         inputs="coherence, detail.core_share",
         rule="Five or more basins, coherence concentrated or spread: echo the engine's label. Its cutoff (core share 0.65) is provisional and swept in the notebook; where it flips the label is dropped and DIS-01's number carries the information.",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="split (DIS-04); fewer than 5 basins; score suppressed; status not ok",
         template="{name}: the basins' values are {concentrated|spread}.",
         in_ui_today="yes: green 'concentrated' and amber 'spread' badges (cheat sheet 4.2)",
         needs_new_data="no"),
]


def evaluate(ctx, row):
    """All DIS statements for one Band A-E row: {id: dict(applies, reason, text, stat)}."""
    res = {}

    def no(i, why):
        res[i] = dict(applies=False, reason=why, text=None, stat=None)

    def yes(i, text, stat):
        res[i] = dict(applies=True, reason=None, text=text, stat=stat)

    method, status = row["method"], row["status"]
    n = ctx["n_units"]
    name = row.get("friendly_name") or row["variable"]
    area = {"buffer": "buffer", "polity": "polity"}.get(ctx["scope"], "area")
    d = row.get("detail") or {}
    dist = d.get("distribution") or {}
    score, coh = row.get("representative_score"), row.get("coherence")

    if method not in CONT:
        base = f"method:{method}"
    elif n == 1:
        base = "one_unit"
    elif status != "ok":
        base = f"status:{status}"
    elif row.get("score_suppressed"):
        base = "suppressed"
    elif score is None:
        base = "no_value"
    else:
        base = None

    big = n is not None and n >= MIN_COHERENT
    for i in ("DIS-01", "DIS-02", "DIS-04", "DIS-06"):
        if base:
            no(i, base)
        elif not big:
            no(i, "fewer_than_5")
    if "DIS-01" not in res:
        if d.get("core_share") is None or d.get("window_lo") is None:
            no("DIS-01", "no_window")
        else:
            yes("DIS-01", f"{name}: {d['core_share']:.0%} of the area lies between the {ordinal(d['window_lo'])} and "
                          f"{ordinal(d['window_hi'])} percentiles.", d["core_share"])
    if "DIS-02" not in res:
        if d.get("p10") is None or d.get("p90") is None:
            no("DIS-02", "no_quantiles")
        else:
            yes("DIS-02", f"{name}: the middle 80% of the area (by weight) lies between the {ordinal(d['p10'])} and "
                          f"{ordinal(d['p90'])} percentiles.", d["p90"] - d["p10"])
    if "DIS-04" not in res:
        if coh != "split":
            no("DIS-04", f"coherence:{coh}")
        else:
            yes("DIS-04", f"{name}: at least half of the area is tied at one value inside the {ordinal(d['window_lo'])} to "
                          f"{ordinal(d['window_hi'])} percentile window, and {1 - d['core_share']:.0%} of the area lies outside it; "
                          f"the headline, the {ordinal(score)} percentile, is the mean over both.", 1 - d["core_share"])
    if "DIS-06" not in res:
        if coh not in ("concentrated", "spread"):
            no("DIS-06", f"coherence:{coh}")
        else:
            yes("DIS-06", f"{name}: the basins' values are {coh}.", d.get("core_share"))

    # DIS-03: min and max, any multi-basin area_weighted row
    if base:
        no("DIS-03", base)
    elif method != "area_weighted":
        no("DIS-03", "no_distribution_block")
    elif dist.get("min") is None or dist.get("max") is None:
        no("DIS-03", "no_min_max")
    else:
        yes("DIS-03", f"{name}: across the {n} basins, values run from the {ordinal(dist['min'])} to the {ordinal(dist['max'])} percentile.",
            dist["max"] - dist["min"])

    # DIS-05: 2 to 4 basins
    if base:
        no("DIS-05", base)
    elif big:
        no("DIS-05", "five_or_more")
    else:
        yes("DIS-05", f"{name}: this {area} has only {n} basins, so no spread label is given (it needs at least {MIN_COHERENT}).", n)
    return res


def evaluate_query(q):
    out = []
    for ctx, row in P.ae_rows(q):
        for i, r in evaluate(ctx, row).items():
            out.append(dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"],
                            variable=row["variable"], method=row["method"], status=row["status"],
                            coherence=row.get("coherence"), id=i, **r))
    return out


def label_consistency(queries, cut=0.65):
    """Counter over eligible rows (5+ basins, ok, not suppressed): does the engine's label agree with core_share >= cut?"""
    import collections
    c = collections.Counter()
    for q in queries:
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            if (ctx["scope"] != "single_basin" and r["method"] in CONT and r["status"] == "ok" and not r.get("score_suppressed")
                    and (ctx["n_units"] or 0) >= MIN_COHERENT and d.get("core_share") is not None and r.get("coherence")):
                c[(r["coherence"], "core>=cut" if d["core_share"] >= cut else "core<cut")] += 1
    return c


def split_checks(queries):
    """For split rows: does the headline score lie inside the core window, and how far is it from p90 and p10?"""
    out = []
    for q in queries:
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            if (r.get("coherence") == "split" and r["status"] == "ok" and not r.get("score_suppressed")
                    and r.get("representative_score") is not None and d.get("window_lo") is not None):
                s = r["representative_score"]
                out.append((ctx["qid"], r["variable"], s, d["window_lo"] <= s <= d["window_hi"],
                            abs(s - d["p90"]), abs(s - d["p10"]), d["core_share"]))
    return out
