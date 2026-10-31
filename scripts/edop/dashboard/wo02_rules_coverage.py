"""WO-02 Step 3, family 4: Coverage and shortfall (how much of the query area the numbers describe).

Three of the four statement types are about the query as a whole (shortfall, basin count, a polity's edge basins) and one is
about a row (a value built from only some of the basins). Query-level items carry variable '(query)'. Rules describe, never
judge (WO constraint 1); every number is printed, and the only display floor (COV-01) is swept in the notebook.
"""
from scripts.edop.dashboard import wo02_payloads as P

FLOOR = 0.01       # COV-01 states a shortfall from 1% of the query area up; swept in the notebook

STATEMENTS = [
    dict(id="COV-01", name="Share of the area outside any basin (shortfall)",
         inputs="shortfall, scope type",
         rule="Buffer or polity with a shortfall of at least 1%: state the share of the area that lies outside any basin (open water, or ground the basin data do not cover) and that the figures describe the rest.",
         applies_to="buffer, polity; L6, L8",
         does_not_apply_when="single basin (shortfall is 0); shortfall below 1% (display floor, swept)",
         template="{share} of this {area} lies outside any basin (open water, or ground the basin data do not cover); the figures describe the rest.",
         in_ui_today="no: shortfall is not displayed (cheat sheet 4.7)",
         needs_new_data="no"),
    dict(id="COV-02", name="How many basins the figures describe",
         inputs="scope.n_units, scope type, level",
         rule="Buffer or polity: state the number of basins and the level; a one-basin buffer says the values are that basin's own.",
         applies_to="buffer, polity; L6, L8",
         does_not_apply_when="single basin scope",
         template="The figures for this {area} describe {n} basins (level {level}). | This {area} contains one basin, so the values are that basin's own.",
         in_ui_today="partly: the Signature tab heading gives 'N basins at Level 06' for buffers and polities (cheat sheet 4.1)",
         needs_new_data="no"),
    dict(id="COV-03", name="A value built from only some of the basins",
         inputs="row n_units, scope.n_units, coverage, shortfall, status = ok",
         rule="A row with status ok whose n_units is smaller than the scope's (some basins have no value): state k of N basins and the share of the basin area that those basins make up (coverage divided by 1 minus shortfall; 'basin area' avoids clashing with 'the area with data' used for one variable in POS-06).",
         applies_to="buffer, polity; area_weighted and class_mixture; L6, L8",
         does_not_apply_when="every basin contributes; status not ok (no_data, low_coverage: Empty cells); dominant_basin rows (coverage is always 1.0 there)",
         template="{name} has a value in {k} of the {N} basins, which make up {share} of the basin area; the figure rests on those basins.",
         in_ui_today="no: for continuous rows the Sandbox shows nothing, and only categorical rows can read low coverage (below half)",
         needs_new_data="no"),
    dict(id="COV-04", name="Edge basins of a polity (marginal exposure)",
         inputs="scope.marginal_exposure {lt_50pct, lt_20pct}",
         rule="Polity: state the weight carried by basins less than half inside the boundary and less than a fifth inside.",
         applies_to="polity; L6, L8",
         does_not_apply_when="buffer or single basin (no such field)",
         template="Basins less than half inside this polity's boundary carry {share} of the weight in these figures, and basins less than a fifth inside carry {share}.",
         in_ui_today="no: scope.marginal_exposure is not displayed (cheat sheet 4.7)",
         needs_new_data="no"),
]


def _pct(x):
    """One decimal below 10% and from 99% up (so 99.8% is not shown as 100%), whole percent otherwise."""
    return f"{x:.1%}" if (x < 0.1 or x >= 0.99) else f"{x:.0%}"


def evaluate_query(q):
    """Query-level records (variable '(query)') for COV-01, 02, 04 and row-level records for COV-03."""
    out = []
    b = q["body"]
    sc, lv = b["scope"]["type"], q["params"]["level"]
    n, sf = b["scope"].get("n_units"), b.get("shortfall") or 0.0
    area = {"buffer": "buffer", "polity": "polity"}.get(sc, "area")
    base = dict(qid=q["id"], scope=sc, level=lv, n_units=n, variable="(query)", method=None, status=None)

    def rec(i, applies, reason=None, text=None, stat=None, **kw):
        out.append(dict(base, id=i, applies=applies, reason=reason, text=text, stat=stat, **kw))

    if sc == "single_basin":
        rec("COV-01", False, "single_basin")
        rec("COV-02", False, "single_basin")
    else:
        if sf < FLOOR:
            rec("COV-01", False, "below_floor", stat=sf)
        else:
            rec("COV-01", True, text=f"{_pct(sf)} of this {area} lies outside any basin (open water, or ground the basin data do not cover); "
                                     "the figures describe the rest.", stat=sf)
        if n == 1:
            rec("COV-02", True, text=f"This {area} contains one basin, so the values are that basin's own.", stat=n)
        else:
            rec("COV-02", True, text=f"The figures for this {area} describe {n} basins (level {lv}).", stat=n)
    me = b["scope"].get("marginal_exposure")
    if sc != "polity":
        rec("COV-04", False, f"scope:{sc}")
    elif not me:
        rec("COV-04", False, "no_field")
    else:
        rec("COV-04", True, text=f"Basins less than half inside this polity's boundary carry {_pct(me['lt_50pct'])} of the weight in these figures, "
                                  f"and basins less than a fifth inside carry {_pct(me['lt_20pct'])}.", stat=me["lt_50pct"])

    # COV-03: one record per Band A-E row
    for ctx, r in P.ae_rows(q):
        row_base = dict(qid=q["id"], scope=sc, level=lv, n_units=n, variable=r["variable"], method=r["method"], status=r["status"])
        k, cov = r.get("n_units"), r.get("coverage")
        if sc == "single_basin":
            why = "single_basin"
        elif r["method"] == "dominant_basin":
            why = "method:dominant_basin"
        elif r["status"] != "ok":
            why = f"status:{r['status']}"
        elif k is None or cov is None or n is None or sf >= 1.0:
            why = "no_value"
        elif k >= n:
            why = "all_basins"
        else:
            share = cov / (1.0 - sf)
            name = r.get("friendly_name") or r["variable"]
            out.append(dict(row_base, id="COV-03", applies=True, reason=None, stat=share,
                            text=f"{name} has a value in {k} of the {n} basins, which make up {_pct(share)} of the basin area; "
                                 "the figure rests on those basins."))
            continue
        out.append(dict(row_base, id="COV-03", applies=False, reason=why, text=None, stat=None))
    return out


def coverage_relation(queries):
    """Counter of how row coverage relates to 1 - shortfall, by (scope, method): equal, below, above."""
    import collections
    c = collections.Counter()
    for q in queries:
        for ctx, r in P.ae_rows(q):
            cov, sf = r.get("coverage"), ctx.get("shortfall") or 0.0
            if cov is None:
                continue
            d = (1 - sf) - cov
            c[(ctx["scope"], r["method"], "equal" if abs(d) < 1e-3 else "below" if d > 0 else "above")] += 1
    return c


def silent_partial(queries):
    """Continuous buffer or polity rows with status ok whose coverage is below 1 - shortfall (some basins have no value).
    Returns (qid, scope, variable, coverage, share of the area with data that has a value)."""
    out = []
    for q in queries:
        for ctx, r in P.ae_rows(q):
            cov, sf = r.get("coverage"), ctx.get("shortfall") or 0.0
            if (ctx["scope"] != "single_basin" and r["method"] in ("area_weighted", "distribution_only") and r["status"] == "ok"
                    and cov is not None and sf < 1.0 and cov < (1 - sf) - 1e-3):
                out.append((ctx["qid"], ctx["scope"], r["variable"], cov, cov / (1 - sf)))
    return out
