"""WO-02 Step 3, family 2: Empty cells (a value is missing, withheld or only partly there, and the payload says why).

One statement type per cause: outside_active_domain (one basin, several), no_data (meaning depends on the variable),
not_areal, low_coverage and score suppressed (two groups). The sea case (rows the engine labels ok although all of the
data-bearing area is at zero) was folded into POS-06 on 2026-10-31. Rules read status and score_suppressed, never a null score alone
(WO constraint 3), and describe without judging (constraint 1).
"""
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import ordinal, CONT, ZERO_AWARE_THRESHOLD

ENGINE_GUARD = 0.90      # the engine's own outside_active_domain threshold on weight_at_zero (engine.py, B1)

# What -9999 means per variable, from the provider's catalog pages (issue 5). Not in the payload: hand-built for the
# ten variables seen with no_data; any other variable is treated as 'missing' with no stated reason.
_SLOPE = ("slope_avg", "slope_upstream")
_SOIL = ("pct_clay", "pct_clay_upstream", "pct_silt", "pct_silt_upstream", "pct_sand", "pct_sand_upstream")
KNOWN_NO_DATA = {"wetland_class", "stream_gradient", *_SLOPE, *_SOIL}


def no_data_meaning(var):
    if var == "wetland_class":
        return "absent", None
    if var in _SLOPE:
        return "missing", "the source leaves out slope over Greenland"
    if var in _SOIL:
        return "missing", "the source soil grid has no data there, mostly deserts and open water"
    return "missing", None


STATEMENTS = [
    dict(id="EMP-01", name="Zero here, no percentile (one basin)",
         inputs="status = outside_active_domain, n_units, weight_at_zero; catalog zero_fraction",
         rule="One basin, status outside_active_domain: state that the value is zero and that no percentile is given, with the share of all basins at the same level that are zero for this variable.",
         applies_to="single basin and one-basin buffer; area_weighted; L6, L8",
         does_not_apply_when="several basins (EMP-02); any other status",
         template="{name} is zero in this basin. No percentile is given: {zf} of all L{level} basins are zero for this variable.",
         in_ui_today="yes: italic 'not present here'; the reason for withholding the percentile is not stated",
         needs_new_data="catalog zero fraction (not in the payload)"),
    dict(id="EMP-02", name="Zero across most of an area, no percentile",
         inputs="status = outside_active_domain, weight_at_zero, n_units, scope type; catalog zero_fraction",
         rule="Several basins, status outside_active_domain: state the share of the area that is zero (weight_at_zero, at least 0.90 by the engine's rule) and that no percentile is given.",
         applies_to="buffer, polity; area_weighted; L6, L8",
         does_not_apply_when="one basin (EMP-01); any other status",
         template="{name} is zero across {share} of this {area}. No percentile is given: {zf} of all L{level} basins are zero for this variable.",
         in_ui_today="yes: italic 'largely absent' with tooltip 'Under 10% of this area has any'; the share is not shown",
         needs_new_data="catalog zero fraction (not in the payload)"),
    dict(id="EMP-03", name="No data (meaning depends on the variable)",
         inputs="status = no_data, variable, n_units, scope type",
         rule="Status no_data: say what the provider's -9999 means for this variable. Wetland class: the source records no wetlands. Slope, stream gradient, soil texture: the source has no value (reason added where the provider documents one).",
         applies_to="all scopes; area_weighted and class_mixture; L6, L8",
         does_not_apply_when="any other status",
         template="absent: The source dataset records no wetlands in {where}, so there is no wetland class. | missing: The source dataset has no {name} value for {where}{ (reason)}.",
         in_ui_today="partly: italic 'no data' for every case; wetland class (absent) and the missing variables read the same",
         needs_new_data="yes: the meaning of -9999 per variable is in the provider's pages, not the payload; a table for the ten variables seen is hand-built in this module. Why 110 non-Greenland basins lack stream gradient is unexplained"),
    dict(id="EMP-04", name="Not defined for an area (polity discharge)",
         inputs="status = not_areal, scope type",
         rule="Status not_areal: say the measure describes a river network, not an area.",
         applies_to="polity; dominant_basin (discharge rows)",
         does_not_apply_when="any other status",
         template="{name} is not reported for a {area}: it describes a river network, not an area.",
         in_ui_today="yes: 'river-network measure, not defined for an area'",
         needs_new_data="no"),
    dict(id="EMP-05", name="Only part of the area has a value (low coverage)",
         inputs="status = low_coverage, coverage, shortfall, representative_raw (modal class)",
         rule="Categorical row with coverage below 0.50: state the covered share, that the class shown is for that part, and where the rest lies (outside any basin: shortfall; in basins with no value: the remainder).",
         applies_to="buffer; class_mixture; L6, L8",
         does_not_apply_when="any other status; polities and single basins have not produced it in the data seen",
         template="Only {coverage} of this {area} has a recorded {name}; the class shown ({label}) is for that part. {outside} lies outside any basin and {rest} is in basins with no value.",
         in_ui_today="partly: modal label plus italic '(low coverage)' with tooltip 'Under half of this area has data'; the cause is not shown",
         needs_new_data="no: coverage and shortfall are in the payload"),
    dict(id="EMP-06", name="No single percentile: two groups",
         inputs="score_suppressed, detail.regimes (centre, weight), n_units, scope type",
         rule="Score suppressed (two regimes): name the two groups with their centres and shares of the area with data, and how far apart the centres are. The call is the engine's (provisional gap 0.50 and weight 0.20 cutoffs); the basin count is stated.",
         applies_to="buffer; area_weighted and distribution_only; L6, L8",
         does_not_apply_when="score not suppressed; polity (modality is skipped); regimes absent",
         template="No single percentile is given for {name}. Across the {n} basins in this {area}, the values fall into two groups: one centred near the {ord} percentile ({share} of the area with data) and one near the {ord} ({share}); the centres are {diff} percentile points apart.",
         in_ui_today="yes: '-' plus 'no single percentile: the area has two distinct groups of values'; centres and shares are in the payload but not shown",
         needs_new_data="no"),
]


def evaluate(ctx, row):
    """All EMP statements for one Band A-E row: {id: dict(applies, reason, text, stat)}."""
    res = {}

    def no(i, why):
        res[i] = dict(applies=False, reason=why, text=None, stat=None)

    def yes(i, text, stat):
        res[i] = dict(applies=True, reason=None, text=text, stat=stat)

    status, method = row["status"], row["method"]
    single = ctx["n_units"] == 1
    lv, n = ctx["level"], ctx["n_units"]
    name = row.get("friendly_name") or row["variable"]
    area = {"buffer": "buffer", "polity": "polity"}.get(ctx["scope"], "area")
    wz, cov, sf = row.get("weight_at_zero"), row.get("coverage"), ctx.get("shortfall") or 0.0
    zf = P.zero_fraction(row["variable"], lv) if method in CONT else None
    zero_clause = f" No percentile is given: {zf:.0%} of all L{lv} basins are zero for this variable." if zf is not None \
        else " No percentile is given."

    # EMP-01 / EMP-02
    if status != "outside_active_domain":
        no("EMP-01", f"status:{status}")
        no("EMP-02", f"status:{status}")
    elif single:
        yes("EMP-01", f"{name} is zero in this basin.{zero_clause}", zf)
        no("EMP-02", "one_unit")
    elif wz is None:
        no("EMP-01", "multi_unit")
        no("EMP-02", "no_weight")
    else:
        no("EMP-01", "multi_unit")
        yes("EMP-02", f"{name} is zero across {wz:.0%} of this {area}.{zero_clause}", wz)

    # EMP-03
    if status != "no_data":
        no("EMP-03", f"status:{status}")
    else:
        where = "this basin" if single else f"any of the {n} basins in this {area}"
        meaning, because = no_data_meaning(row["variable"])
        if meaning == "absent":
            yes("EMP-03", f"The source dataset records no wetlands in {where}, so there is no wetland class.", None)
        else:
            yes("EMP-03", f"The source dataset has no {name} value for {where}" + (f" ({because})" if because else "") + ".", None)

    # EMP-04
    if status != "not_areal":
        no("EMP-04", f"status:{status}")
    else:
        yes("EMP-04", f"{name} is not reported for a {area}: it describes a river network, not an area.", None)

    # EMP-05
    if status != "low_coverage":
        no("EMP-05", f"status:{status}")
    else:
        label = row.get("representative_raw")
        outside, rest = sf, max(0.0, 1.0 - (cov or 0.0) - sf)
        nv = "in basins where the source records no wetlands" if row["variable"] == "wetland_class" else "in basins with no value"
        pct = f"{cov:.0%}"
        if pct == "50%" and cov < 0.5:
            pct = f"{cov:.2%}"
        t = f"Only {pct} of this {area} has a recorded {name}; the class shown ({label}) is for that part."
        if outside >= 0.005 and rest >= 0.005:
            t += f" {outside:.0%} of the {area} lies outside any basin and {rest:.0%} is {nv}."
        elif outside >= 0.005:
            t += " The rest lies outside any basin."
        elif rest >= 0.005:
            t += f" The rest is {nv}."
        yes("EMP-05", t, cov)

    # EMP-06
    if status != "ok" or not row.get("score_suppressed"):
        no("EMP-06", "not_suppressed" if status == "ok" else f"status:{status}")
    else:
        reg = sorted((row.get("detail") or {}).get("regimes") or [], key=lambda r: r["center"])
        if len(reg) != 2:
            no("EMP-06", "no_regimes")
        else:
            lo, hi = reg
            diff = hi["center"] - lo["center"]
            za6 = zf is not None and zf >= ZERO_AWARE_THRESHOLD
            lo_txt = ("one where the value is zero" if za6 and lo["center"] == 0
                      else f"one centred near the {ordinal(lo['center'])} percentile")
            hi_txt = f"one centred near the {ordinal(hi['center'])} percentile"
            unit = "point" if round(diff) == 1 else "points"
            yes("EMP-06", f"No single percentile is given for {name}. Across the {n} basins in this {area}, the values fall "
                          f"into two groups: {lo_txt} ({lo['weight']:.0%} of the area with data) and {hi_txt} "
                          f"({hi['weight']:.0%}); the centres are {diff:.0f} percentile {unit} apart.", diff)

    return res


def evaluate_query(q):
    """Flat list of dicts, one per (row, statement id), for one query."""
    out = []
    for ctx, row in P.ae_rows(q):
        for i, r in evaluate(ctx, row).items():
            out.append(dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"],
                            variable=row["variable"], method=row["method"], status=row["status"],
                            suppressed=bool(row.get("score_suppressed")), id=i, **r))
    return out


def guard_candidates(queries):
    """Rows the engine's zero guard (and the sea case, now POS-06) could apply to: buffer/polity area_weighted zero-aware rows with a weight and coverage."""
    out = []
    for q in queries:
        for ctx, row in P.ae_rows(q):
            if (row["method"] == "area_weighted" and ctx["n_units"] != 1 and row["status"] in ("ok", "outside_active_domain")
                    and row.get("weight_at_zero") is not None and row.get("coverage")):
                zf = P.zero_fraction(row["variable"], ctx["level"])
                if zf is not None and zf >= ZERO_AWARE_THRESHOLD:
                    out.append((ctx["qid"], ctx["scope"], row["variable"], row["status"],
                                row["weight_at_zero"], row["weight_at_zero"] / row["coverage"]))
    return out


def low_coverage_causes(queries):
    """(qid, variable, coverage, shortfall, rest) for every low_coverage row; rest = share in basins with no value."""
    out = []
    for q in queries:
        for ctx, row in P.ae_rows(q):
            if row["status"] == "low_coverage":
                sf = ctx.get("shortfall") or 0.0
                out.append((ctx["qid"], row["variable"], row["coverage"], sf, max(0.0, 1.0 - row["coverage"] - sf)))
    return out
