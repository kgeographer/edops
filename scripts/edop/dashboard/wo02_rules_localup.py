"""WO-02 Step 3, family 3: Local and upstream (a variable and its `_upstream` pair).

An item is either a pair (a local row and its upstream row, found through the catalog: same schema_key, su s and u) or a
continuous variable with a local value only. Rules describe the gap in percentile points and never judge it
(WO constraint 1). Whether two values "agree" or "differ" depends on a cutoff, so the statements print the gap and the
notebook sweeps a grid of cutoffs instead of choosing one.
"""
import pandas as pd
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import ordinal, fmt_num

CONT = ("area_weighted", "distribution_only", "dominant_basin")

STATEMENTS = [
    dict(id="LU-01", name="Percentile gap, local versus upstream (one basin)",
         inputs="representative_score of the local row and of its _upstream row; n_units; both status ok, neither suppressed, neither at percentile 0",
         rule="One basin, both rows have a percentile above 0: state both percentiles and the gap in percentile points, and which side is higher. No agree or differ label (cutoff, swept).",
         applies_to="single basin and one-basin buffer; the 13 variables that have an upstream pair; L6, L8",
         does_not_apply_when="several basins (LU-02); either side empty, suppressed or at percentile 0 (LU-04)",
         template="{name}: upstream ranks at the {ord} percentile and local at the {ord}, {gap} percentile points {higher|lower} upstream.",
         in_ui_today="no: the two rows are listed separately in the Signature tab; nothing links or compares them (cheat sheet 2.2)",
         needs_new_data="no"),
    dict(id="LU-02", name="Percentile gap, local versus upstream (area)",
         inputs="representative_score of both rows (area-weighted means); n_units",
         rule="Several basins, both rows have a percentile above 0, neither suppressed: state both area-weighted mean percentiles and the gap.",
         applies_to="buffer, polity; the 13 paired variables; L6, L8",
         does_not_apply_when="one basin (LU-01); either side empty, suppressed or at percentile 0 (LU-04)",
         template="{name}: across the {n} basins in this {area}, the upstream mean percentile is the {ord} and the local the {ord}, {gap} percentile points {higher|lower} upstream.",
         in_ui_today="no",
         needs_new_data="no"),
    dict(id="LU-03", name="Raw values, local versus upstream (one basin)",
         inputs="representative_raw and units of both rows",
         rule="One basin, both raw values present: state both with the local row's units.",
         applies_to="single basin and one-basin buffer; the 13 paired variables",
         does_not_apply_when="several basins (no native-unit value); either raw missing",
         template="{name}: {raw}{ units} in this basin and {raw}{ units} across everything upstream.",
         in_ui_today="no: each row shows its own raw value; the pair is not shown together",
         needs_new_data="display scale per variable not verified (raw printed as stored)"),
    dict(id="LU-04", name="One side has no usable percentile",
         inputs="status and score_suppressed of both rows, scores, weight_at_zero, scope",
         rule="Either row is empty (no data, outside_active_domain), suppressed or at percentile 0: say what each side is, using the usable side's percentile where there is one.",
         applies_to="all scopes with a paired variable",
         does_not_apply_when="both sides have a usable percentile (LU-01 or LU-02)",
         template="{name}: local {state}; upstream {state}.",
         in_ui_today="no",
         needs_new_data="no"),
    dict(id="LU-05", name="No upstream value exists",
         inputs="catalog: the variable has no upstream counterpart",
         rule="A continuous variable with a local value only: say there is no separate upstream value. The wording does not say the variable covers this basin only: a variable such as river discharge may already include everything upstream (what area each variable covers is not in the payload).",
         applies_to="the 15 continuous local-only variables (e.g. elevation, runoff, groundwater depth, discharge, temperature extremes)",
         does_not_apply_when="the variable has an upstream pair; categorical and flag rows (never paired, not items here)",
         template="There is no separate upstream value for {name}.",
         in_ui_today="no",
         needs_new_data="no: the pairing is in the catalog (schema_key and su)"),
]

_PARTNER = {}


def partners(level):
    """{local variable: upstream variable} from the engine catalog (same schema_key, su s and u)."""
    if level not in _PARTNER:
        cat = P.catalog(level)
        up = {(r.schema_key): k for k, r in cat.iterrows() if r.su == "u"}
        _PARTNER[level] = {k: up[r.schema_key] for k, r in cat.iterrows() if r.su == "s" and r.schema_key in up}
    return _PARTNER[level]


def _state(row, single):
    """(usable, phrase) for one side of a pair."""
    st, sc = row["status"], row.get("representative_score")
    if st == "outside_active_domain":
        wz = row.get("weight_at_zero")
        return False, ("is zero" if single or wz is None else f"is zero across {wz:.0%} of the area")
    if st == "no_data":
        return False, "has no data"
    if st != "ok":
        return False, f"has status {st}"
    if row.get("score_suppressed"):
        return False, "has no single percentile (two groups)"
    if sc is None:
        return False, "has no percentile"
    if sc == 0:
        return False, "is at percentile 0"
    return True, (f"ranks at the {ordinal(sc)} percentile" if single else f"averages the {ordinal(sc)} percentile")


def _code(row):
    """Short state of one side: usable, zero (percentile 0), oad (outside_active_domain), no_data, suppressed, other."""
    st = row["status"]
    if st == "outside_active_domain":
        return "oad"
    if st == "no_data":
        return "no_data"
    if st != "ok":
        return "other"
    if row.get("score_suppressed"):
        return "suppressed"
    sc = row.get("representative_score")
    if sc is None:
        return "other"
    return "zero" if sc == 0 else "usable"


def evaluate(ctx, local, up):
    """Statements for one item: `up` is the upstream row, or None for a local-only variable."""
    res = {}

    def no(i, why):
        res[i] = dict(applies=False, reason=why, text=None, stat=None, signed=None)

    def yes(i, text, stat=None, signed=None):
        res[i] = dict(applies=True, reason=None, text=text, stat=stat, signed=signed)

    single = ctx["n_units"] == 1
    name = local.get("friendly_name") or local["variable"]
    area = {"buffer": "buffer", "polity": "polity"}.get(ctx["scope"], "area")
    if up is None:
        for i in ("LU-01", "LU-02", "LU-03", "LU-04"):
            no(i, "no_partner")
        yes("LU-05", f"There is no separate upstream value for {name}.")
        return res
    no("LU-05", "has_partner")
    ul, pl = _state(local, single)
    uu, pu = _state(up, single)
    if ul and uu:
        sl, su = local["representative_score"], up["representative_score"]
        gap = su - sl                              # precise gap: used for the sweep (stat) and the sign
        shown = round(su) - round(sl)              # the gap between the percentiles as displayed, so the sentence adds up
        side = "higher" if shown > 0 else "lower"
        gtxt = f"{abs(shown)} percentile point{'' if abs(shown) == 1 else 's'} {side} upstream"
        if single:
            yes("LU-01", f"{name}: upstream ranks at the {ordinal(su)} percentile and local at the {ordinal(sl)}, {gtxt}."
                if shown != 0 else f"{name}: upstream and local both rank at the {ordinal(sl)} percentile.", abs(gap), gap)
            no("LU-02", "one_unit")
        else:
            yes("LU-02", f"{name}: across the {ctx['n_units']} basins in this {area}, the upstream mean percentile is the "
                         f"{ordinal(su)} and the local the {ordinal(sl)}, {gtxt}."
                if shown != 0 else f"{name}: across the {ctx['n_units']} basins in this {area}, the upstream and local mean percentiles are both the {ordinal(sl)}.",
                abs(gap), gap)
            no("LU-01", "multi_unit")
        no("LU-04", "both_usable")
    else:
        no("LU-01", "side_not_usable")
        no("LU-02", "side_not_usable")
        yes("LU-04", f"{name}: local {pl}; upstream {pu}.")
    rl, ru = local.get("representative_raw"), up.get("representative_raw")
    if not single:
        no("LU-03", "multi_unit")
    elif rl is None or ru is None:
        no("LU-03", "no_raw")
    else:
        un = f" {local['units']}" if local.get("units") else ""
        yes("LU-03", f"{name}: {fmt_num(rl)}{un} in this basin and {fmt_num(ru)}{un} across everything upstream.")
    return res


def evaluate_query(q):
    """Flat list of dicts, one per (item, statement id). An item is a pair or a continuous local-only variable."""
    out = []
    rows = P.ae_rows(q)
    if not rows:
        return out
    by = {r["variable"]: r for _, r in rows}
    ctx0 = rows[0][0]
    cat = P.catalog(ctx0["level"])
    pmap = partners(ctx0["level"])
    for ctx, r in rows:
        v = r["variable"]
        if v not in cat.index or cat.loc[v, "su"] != "s":
            continue
        if v in pmap and pmap[v] in by:
            up = by[pmap[v]]
        elif r["method"] in CONT:
            up = None
        else:
            continue
        for i, res in evaluate(ctx, r, up).items():
            out.append(dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"],
                            variable=v, method=r["method"], status=r["status"],
                            up_status=(up["status"] if up else None), paired=up is not None,
                            lcode=_code(r), ucode=(_code(up) if up else None), id=i, **res))
    return out


def gap_summary(df):
    """Per paired variable and query kind: n, weighted median signed gap (upstream minus local), share with upstream higher,
    weighted median absolute gap. Rows where both sides have a usable percentile only."""
    d = df[df.id.isin(["LU-01", "LU-02"]) & df.applies]
    rows = []
    for (var, kind), g in d.groupby(["variable", "kind"]):
        sg, w = g.signed.astype(float), g.w
        rows.append(dict(variable=var, kind=kind, n=len(g), median_signed=P.wquantile(sg, w, 0.5),
                         up_higher=float((w * (sg > 0)).sum() / w.sum()),
                         median_abs=P.wquantile(g.stat.astype(float), w, 0.5)))
    return pd.DataFrame(rows)


def state_crosstab(df):
    """Weighted share of paired items by (local state, upstream state), within each query kind."""
    d = df[(df.id == "LU-04") & df.paired]
    tot = d.groupby("kind").w.sum()
    num = d.groupby(["kind", "lcode", "ucode"]).w.sum()
    return (num / num.index.get_level_values("kind").map(tot).values).unstack("ucode").fillna(0.0)
