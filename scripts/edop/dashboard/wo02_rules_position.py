"""WO-02 Step 3, family 1: Position statements (percentile with its reference frame, raw value, zero-aware branch).

Each rule reads one Band A-E row plus its query context and returns applies / reason / text / stat. Rules branch on
scope (n_units), method, status and score_suppressed, never on a null score alone (WO constraint 3). They describe a
position and never judge it (constraint 1). POS-06 was tested with a soft "Most of / Part of" wording; the cutoff sweep
(notebook) shows it flips, so the statement gives the number alone.
"""
import math
from scripts.edop.dashboard import wo02_payloads as P

CONT = ("area_weighted", "distribution_only")
CONT1 = CONT + ("dominant_basin",)       # single-unit rules also cover the dominant-basin discharge rows
ZERO_AWARE_THRESHOLD = 0.20              # the engine's own threshold (engine.rank_expr); the zero fraction comes from the catalog
FLOOR = 0.01                             # POS-06 states a share only from 1% of the area with data up (display floor)

STATEMENTS = [
    dict(id="POS-01", name="Percentile with reference frame (one basin)",
         inputs="representative_score, level, n_units, status, method, representative_raw; catalog zero_fraction",
         rule="One basin, continuous variable, status ok, raw not 0, variable not zero-aware: state the percentile and the frame (all basins at the same level worldwide).",
         applies_to="single basin and one-basin buffer; area_weighted, distribution_only, dominant_basin; L6, L8",
         does_not_apply_when="multi-basin (POS-02); status not ok; raw is 0 (POS-04); zero-aware variable (POS-05); categorical or flag (no percentile)",
         template="{name} ranks at the {ord} percentile among all L{level} basins worldwide.",
         in_ui_today="yes: 'raw units . N.N percentile' with a 0-100 dot track (cheat sheet 4.2); the UI does not name the level (2.5)",
         needs_new_data="no"),
    dict(id="POS-02", name="Percentile for an area (area-weighted mean)",
         inputs="representative_score, level, n_units, scope type, score_suppressed; catalog zero_fraction",
         rule="Several basins, continuous variable, status ok, score present (not suppressed): state the area-weighted mean of the member basins' percentiles, with the frame and the basin count. For a zero-aware variable add that a basin that is zero is at 0 and the others are ranked among the non-zero basins.",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="one basin; score suppressed (two groups, see Distribution family); score exactly 0 (everything is at the bottom: POS-06 states it); status not ok; categorical or flag",
         template="Across the {n} basins in this {area}, {name} averages the {ord} percentile among all L{level} basins worldwide (area-weighted mean of the basins' percentiles).",
         in_ui_today="partly: '*N.N* percentile' plus a coherence badge; neither the 'mean of member percentiles' nor the level is named in the row",
         needs_new_data="no"),
    dict(id="POS-03", name="Raw value with units (one basin)",
         inputs="representative_raw, units, n_units, status, method",
         rule="One basin, continuous variable, raw present: state the value as stored, with units when the payload has them.",
         applies_to="single basin and one-basin buffer; area_weighted, distribution_only, dominant_basin",
         does_not_apply_when="multi-basin (no native-unit value); status not ok; categorical (label, see Categorical) or flag",
         template="{name} is {raw}{ units}.",
         in_ui_today="yes: same row as POS-01",
         needs_new_data="display scale per variable is not verified: the raw value is printed as stored (a few variables are stored with a scale factor)"),
    dict(id="POS-04", name="Zero here (one basin)",
         inputs="representative_raw, status, n_units",
         rule="One basin, continuous variable, status ok, raw exactly 0 and percentile 0. A raw 0 with a percentile above 0 (elevation minimum 0 m is sea level; 0 degrees C) is an ordinary value and falls under POS-01 and POS-03.",
         applies_to="single basin and one-basin buffer; area_weighted, distribution_only, dominant_basin",
         does_not_apply_when="multi-basin; status not ok; raw not 0, or raw 0 with a percentile above 0",
         template="{name} is zero in this basin.",
         in_ui_today="partly: the row shows raw 0 and percentile 0; status outside_active_domain shows 'not present here'; no 'zero' sentence",
         needs_new_data="no"),
    dict(id="POS-05", name="Rank among the non-zero basins (zero-aware, one basin)",
         inputs="representative_score, representative_raw, units, level; catalog zero_fraction (>= 0.20)",
         rule="One basin, continuous zero-aware variable (global zero fraction at least 0.20), raw above 0: state the value and that the percentile ranks it among the non-zero basins, with the share of basins that are zero. What zero means differs by variable (absence for karst or cropland, distance zero for flow distance to the outlet), so the wording does not say 'none'.",
         applies_to="single basin and one-basin buffer; zero-aware variables only; L6, L8",
         does_not_apply_when="multi-basin; raw is 0 (POS-04); variable not zero-aware (POS-01)",
         template="{name} is {raw}{ units}. Of all L{level} basins, {zf} are zero for this variable; ranked among the non-zero basins, this basin is at the {ord} percentile.",
         in_ui_today="no: the UI shows the percentile without saying zeros were set aside",
         needs_new_data="yes: the payload does not say which variables are zero-aware or their zero fraction (Step 2 cell 10); catalog lookup (zero_fraction_s/u_L6/L8) now, or a payload field later (engine change). A per-variable meaning of zero (absent, or a real zero such as distance) would be needed to say more than 'zero'"),
    dict(id="POS-06", name="Share of an area at the bottom of the ranking",
         inputs="weight_at_zero, coverage, n_units, status, method",
         rule="Several basins, continuous variable, status ok: state the share of the area with data whose basins are at percentile 0 (weight_at_zero divided by coverage, because in a buffer weight_at_zero is a share of the whole circle, sea included). The number is stated alone: a 'Most of / Part of' wording was tested and flips (see sweep). Not stated below a 1% share. This also covers rows the engine labels ok although all of the data-bearing area is at zero because sea kept its outside_active_domain guard from firing (formerly EMP-07, folded in 2026-10-31): the share is true at any guard threshold, and whether to withhold the percentile is a dashboard decision, not a rule here.",
         applies_to="buffer, polity; area_weighted, distribution_only; L6, L8",
         does_not_apply_when="one basin (POS-04); status not ok; coverage 0 or weight_at_zero absent (distribution_only rows carry none); share below 1%",
         template="{share} of the area with data is at percentile 0, the bottom of the world ranking for {name}.",
         in_ui_today="no: weight_at_zero is not displayed (cheat sheet 4.7)",
         needs_new_data="no; the division by coverage is derived here, not given by the payload. Dashboard decision (not a rule): whether to withhold the percentile where the share is 0.90 or more of the data-bearing area"),
    dict(id="POS-07", name="Dominant basin's discharge value",
         inputs="representative_raw, units, representative_score, level, n_units, status, method=dominant_basin",
         rule="Several basins, dominant_basin row, status ok: state the value and percentile of the basin with the highest annual discharge in the area.",
         applies_to="buffer; discharge rows (dominant_basin); L6, L8",
         does_not_apply_when="one basin (POS-01/03); polity (status not_areal); any status not ok",
         template="In the basin with the highest annual discharge in this area, {name} is {raw}{ units} (the {ord} percentile among all L{level} basins).",
         in_ui_today="yes: 'raw units . N.N percentile' + 'basin id' (hidden for one basin)",
         needs_new_data="no"),
]


def fmt_num(v):
    """Number as text: whole numbers and thousands separators from 10 up, 2 decimals from 1, 2 significant digits below 1."""
    if v is None:
        return None
    a = abs(v)
    if a == 0:
        return "0"
    if a >= 1000:
        return f"{v:,.0f}"
    if a >= 100 or float(v).is_integer():
        return f"{v:.0f}"
    if a >= 10:
        return f"{v:.1f}"
    if a >= 1:
        return f"{v:.2f}".rstrip("0").rstrip(".")
    digits = 1 - math.floor(math.log10(a))
    return f"{v:.{digits}f}".rstrip("0").rstrip(".")


def ordinal(n):
    n = int(round(n))
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def evaluate(ctx, row):
    """All POS statements for one row: {id: dict(applies, reason, text, stat)}."""
    res = {}

    def no(i, why):
        res[i] = dict(applies=False, reason=why, text=None, stat=None)

    def yes(i, text, stat):
        res[i] = dict(applies=True, reason=None, text=text, stat=stat)

    method, status = row["method"], row["status"]
    single = ctx["n_units"] == 1
    lv = ctx["level"]
    name = row.get("friendly_name") or row["variable"]
    score, raw = row.get("representative_score"), row.get("representative_raw")
    wz, cov = row.get("weight_at_zero"), row.get("coverage")
    units = f" {row['units']}" if row.get("units") else ""
    area = {"buffer": "buffer", "polity": "polity"}.get(ctx["scope"], "area")

    cat_reason = None
    if method not in CONT1:
        cat_reason = f"method:{method}"
    elif status != "ok":
        cat_reason = f"status:{status}"
    za, zf = (False, None)
    if method in CONT:
        zf = P.zero_fraction(row["variable"], lv)
        za = zf is not None and zf >= ZERO_AWARE_THRESHOLD

    # POS-01 / 03 / 04 / 05: one basin
    for i in ("POS-01", "POS-03", "POS-04", "POS-05"):
        if cat_reason:
            no(i, cat_reason)
        elif not single:
            no(i, "multi_unit")
    if "POS-01" not in res:
        if raw is None or score is None:
            no("POS-01", "no_value")
        elif raw == 0 and score == 0:
            no("POS-01", "zero_value")
        elif za:
            no("POS-01", "zero_aware_variable")
        else:
            yes("POS-01", f"{name} ranks at the {ordinal(score)} percentile among all L{lv} basins worldwide.", score)
    if "POS-03" not in res:
        if raw is None:
            no("POS-03", "no_value")
        else:
            yes("POS-03", f"{name} is {fmt_num(raw)}{units}.", raw)
    if "POS-04" not in res:
        if raw == 0 and score == 0:
            yes("POS-04", f"{name} is zero in this basin.", 0)
        else:
            no("POS-04", "not_zero")
    if "POS-05" not in res:
        if not za:
            no("POS-05", "not_zero_aware")
        elif raw is None or score is None:
            no("POS-05", "no_value")
        elif raw == 0 and score == 0:
            no("POS-05", "zero_value")
        else:
            yes("POS-05", f"{name} is {fmt_num(raw)}{units}. Of all L{lv} basins, {zf:.0%} are zero for this variable; "
                          f"ranked among the non-zero basins, this basin is at the {ordinal(score)} percentile.", score)

    # POS-02: area percentile
    if method not in CONT:
        no("POS-02", f"method:{method}")
    elif single:
        no("POS-02", "one_unit")
    elif status != "ok":
        no("POS-02", f"status:{status}")
    elif row.get("score_suppressed"):
        no("POS-02", "suppressed")
    elif score is None:
        no("POS-02", "no_value")
    elif score == 0:
        no("POS-02", "all_at_bottom")
    else:
        t = (f"Across the {ctx['n_units']} basins in this {area}, {name} averages the {ordinal(score)} percentile "
             f"among all L{lv} basins worldwide (area-weighted mean of the basins' percentiles).")
        if za:
            t += " For this variable a basin that is zero is at percentile 0 and the others are ranked among the non-zero basins."
        yes("POS-02", t, score)

    # POS-06: share at the bottom
    if method not in CONT:
        no("POS-06", f"method:{method}")
    elif single:
        no("POS-06", "one_unit")
    elif status != "ok":
        no("POS-06", f"status:{status}")
    elif wz is None or not cov:
        no("POS-06", "no_weight")
    else:
        adj = wz / cov
        if adj < FLOOR:
            no("POS-06", "below_floor")
        else:
            yes("POS-06", f"{adj:.0%} of the area with data is at percentile 0, the bottom of the world ranking for {name}.", adj)

    # POS-07: dominant basin
    if method != "dominant_basin":
        no("POS-07", f"method:{method}")
    elif single:
        no("POS-07", "one_unit")
    elif status != "ok":
        no("POS-07", f"status:{status}")
    elif raw is None or score is None:
        no("POS-07", "no_value")
    else:
        yes("POS-07", f"In the basin with the highest annual discharge in this area, {name} is {fmt_num(raw)}{units} "
                      f"(the {ordinal(score)} percentile among all L{lv} basins).", score)
    return res


def evaluate_query(q):
    """Flat list of dicts, one per (row, statement id), for one query."""
    out = []
    for ctx, row in P.ae_rows(q):
        for i, r in evaluate(ctx, row).items():
            out.append(dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"],
                            variable=row["variable"], method=row["method"], status=row["status"], id=i, **r))
    return out


# ---- Position-specific checks used by the notebook -------------------------------------------------------

def bottom_shares(queries):
    """(query id, weight-free) list of (qid, scope, variable, adjusted share) for every row POS-06 could consider,
    before the display floor. Used to sweep the floor."""
    out = []
    for q in queries:
        for ctx, row in P.ae_rows(q):
            if (row["method"] in CONT and row["status"] == "ok" and ctx["n_units"] != 1
                    and row.get("weight_at_zero") is not None and row.get("coverage")):
                out.append((ctx["qid"], ctx["scope"], row["variable"], row["weight_at_zero"] / row["coverage"]))
    return out


def single_unit_zero_crosstab(queries):
    """Counter of (raw == 0, score == 0) over one-basin continuous ok rows."""
    import collections
    c = collections.Counter()
    for q in queries:
        for ctx, row in P.ae_rows(q):
            if ctx["n_units"] == 1 and row["method"] in CONT1 and row["status"] == "ok":
                c[(row["representative_raw"] == 0, row["representative_score"] == 0)] += 1
    return c


def sea_guard_misses(queries, guard=0.90):
    """Buffer rows of zero-aware variables whose data-bearing area is at percentile 0 for `guard` or more but whose
    weight_at_zero (a share of the whole circle) is below it, so the engine's outside_active_domain guard did not fire."""
    out = []
    for q in queries:
        for ctx, row in P.ae_rows(q):
            if ctx["scope"] == "buffer" and row["method"] == "area_weighted" and row["status"] == "ok" \
                    and row.get("weight_at_zero") is not None and row.get("coverage"):
                zf = P.zero_fraction(row["variable"], ctx["level"])
                if zf is not None and zf >= ZERO_AWARE_THRESHOLD \
                        and row["weight_at_zero"] / row["coverage"] >= guard > row["weight_at_zero"]:
                    out.append((ctx["qid"], round(ctx["shortfall"], 2), row["variable"], round(row["weight_at_zero"], 3)))
    return out
