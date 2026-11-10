"""WO-02 Step 3, family 9: Band T (LMR climate, HYDE land use, eVolv2k volcanic forcing over a year span).

Band T rows have no percentile and no friendly name, so labels are supplied here (from outside the payload). Each source has its
own structure: LMR rows are yearly footprint means as anomalies against the 850-1850 CE CCSM4 reference, with the spread across
grid cells in detail.distribution; HYDE rows are km² totals per epoch with a per-cell distribution; eVolv2k rows are bare events
(year and Tg S). The rules describe and never judge (WO constraint 1). The evidence is the Band T fixtures only (no population sample).
"""
from scripts.edop.dashboard import wo02_payloads as P
from scripts.edop.dashboard.wo02_rules_position import fmt_num

LMR_NAMES = {"lmr_air": "LMR air temperature", "lmr_prate": "LMR precipitation rate", "lmr_pdsi": "LMR drought index (PDSI)"}
HYDE_NAMES = {"hyde_cropland": "cropland", "hyde_grazing": "grazing land", "hyde_pasture": "pasture", "hyde_rangeland": "rangeland"}
LMR_FIRST, LMR_LAST = 0, 1998         # LMR record in the payloads (cheat sheet 3.2; F41 ends at 1998, F42 starts at 0)
EV_FIRST, EV_LAST = -491, 1890        # eVolv2k record (the database table: 255 events from -491 to 1890)

STATEMENTS = [
    dict(id="BT-01", name="LMR anomaly over the span, per variable",
         inputs="lmr_* rows: year, representative_raw, units; caveat (reference frame)",
         rule="LMR rows present: state the mean of the yearly anomalies over the covered years, the lowest and highest year, and the reference frame (850-1850 CE CCSM4); a single year says that year's anomaly. The sign is in the number.",
         applies_to="single basin, buffer, polity; air temperature, precipitation rate, PDSI; spans inside 0 to 1998 CE",
         does_not_apply_when="no LMR rows (BCE span, span after 1998)",
         template="{name}, {from} to {to}: the yearly anomaly averages {n} {units}, lowest {n} in {year}, highest {n} in {year}, against the 850-1850 CE reference. | In {year} the anomaly is {n} ...",
         in_ui_today="yes: a footprint histogram for the middle year, a year slider and a time series with a p10 to p90 band",
         needs_new_data="readable names for the three LMR variables are not in the payload"),
    dict(id="BT-02", name="LMR spread across grid cells (middle year)",
         inputs="lmr_* rows: detail.distribution (n_units, min, max)",
         rule="Two or more grid cells: state the lowest and highest cell value in the middle year of the covered years (the year the Sandbox histogram opens on).",
         applies_to="single basin, buffer, polity; LMR variables",
         does_not_apply_when="one grid cell; no LMR rows",
         template="{name}: in {year}, the values across the {n} grid cells range from {n} to {n} {units}.",
         in_ui_today="yes: the footprint histogram for the middle year",
         needs_new_data="no"),
    dict(id="BT-03", name="How many LMR grid cells the footprint touches",
         inputs="lmr_* rows: detail.distribution.n_units and low_resolution",
         rule="LMR rows present: state the number of grid cells (each 2 degrees wide) and, when the engine's low_resolution flag is set, that it marks this low resolution. The flag appears always true at a single basin (even for the largest L6 basin, 11 cells) and false only for a polity or a large buffer.",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="no LMR rows",
         template="The footprint touches {n} LMR grid cells (each 2 degrees wide), so each yearly value is built from {n} cells; the engine marks this low resolution.",
         in_ui_today="partly: the LMR header shows 'N cells'; the low_resolution flag is not shown",
         needs_new_data="no"),
    dict(id="BT-04", name="The span runs outside the LMR record",
         inputs="temporal span; years present in the lmr_* rows; the LMR record (0 to 1998 CE)",
         rule="A span not wholly inside 0 to 1998 CE: state the covered part and that there are no values for the rest, or that the span lies outside the record. The payload returns only the covered years and gives no placeholder.",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="span wholly inside the record",
         template="LMR covers {from} to {to} of the span {from} to {to} (the record runs 0 to 1998 CE); there are no values for the rest. | The span lies outside the LMR record, so there are no LMR values.",
         in_ui_today="no: the Sandbox shows the covered years; the gap is not stated",
         needs_new_data="the record bounds are not in the payload (taken from the cheat sheet and confirmed by two fixtures)"),
    dict(id="BT-05", name="HYDE land use in one epoch",
         inputs="hyde_* rows: epoch_year, representative_raw (km²)",
         rule="Exactly one HYDE epoch: state the four totals in km² for that epoch.",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="two or more epochs (BT-06)",
         template="HYDE land use ({epoch} epoch): cropland {n} km², grazing land {n} km², pasture {n} km², rangeland {n} km².",
         in_ui_today="yes: a table, one column per epoch, with km² sums",
         needs_new_data="no"),
    dict(id="BT-06", name="HYDE change between the first and last epoch",
         inputs="hyde_* rows: epoch_year, representative_raw",
         rule="Two or more epochs: state the first and last epoch's total for each land-use type and the change between them (in km², and as a share of the first when it is above zero).",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="a single epoch (BT-05)",
         template="HYDE {land use}: {n} km² in {epoch}, {n} km² in {epoch}, a change of {n} km² ({n}%) across {n} epochs.",
         in_ui_today="partly: the table shows every epoch; the change is not stated",
         needs_new_data="no"),
    dict(id="BT-07", name="No HYDE epoch inside the span (nearest epoch shown)",
         inputs="caveats.hyde_nearest_year; the epoch shown; the span",
         rule="The payload carries hyde_nearest_year: state that no epoch falls in the span, which epoch is shown and how many years it lies before or after the span.",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="an epoch lies inside the span",
         template="No HYDE epoch falls within the span; the nearest, the {epoch} epoch, is {n} years {before|after} it.",
         in_ui_today="yes: a '~' prefix and a footnote on the epoch",
         needs_new_data="no"),
    dict(id="BT-08", name="HYDE 1950 caveat",
         inputs="caveats.hyde_caveat",
         rule="The payload carries hyde_caveat (the 1950 epoch): quote it. It sits on the 1950 epoch's rows only.",
         applies_to="spans containing 1950",
         does_not_apply_when="no hyde_caveat",
         template="HYDE 1950 epoch: {the payload's caveat text}.",
         in_ui_today="no: the caveat text is in the payload and is not displayed",
         needs_new_data="no"),
    dict(id="BT-09", name="Volcanic events in the span (count, largest, timing)",
         inputs="evolv2k_vssi rows: year, representative_raw (Tg S)",
         rule="Events present: state the count and the largest one (year, size in Tg S, and how many years into the span it falls).",
         applies_to="single basin, buffer, polity (a global series, the same for any place)",
         does_not_apply_when="no events (BT-10)",
         template="{n} volcanic events in {from} to {to}: the largest, in {year}, injected {n} Tg S of stratospheric sulfur ({n} years into the span). | One volcanic event ...",
         in_ui_today="yes: a table of year and VSSI (events of 5 Tg S or more, with a 'show all' link)",
         needs_new_data="no"),
    dict(id="BT-10", name="No volcanic events (or span outside the record)",
         inputs="evolv2k_vssi rows (none); the span; the record (491 BCE to 1890 CE)",
         rule="No event rows: say no events are recorded in the span, or that the span lies (partly) outside the record. A span with no events returns no rows and no placeholder.",
         applies_to="single basin, buffer, polity",
         does_not_apply_when="events present",
         template="No volcanic events are recorded in {from} to {to}. | The span lies outside the eVolv2k record (491 BCE to 1890 CE).",
         in_ui_today="partly: the table is empty",
         needs_new_data="the record bounds are not in the payload (taken from the database table)"),
]


def _y(y, ce=False):
    """A year as the Sandbox writes it: negative years are BCE; ce=True adds CE to a positive year (for spans that cross zero)."""
    return f"{abs(y)} BCE" if y < 0 else (f"{y} CE" if ce else str(y))


def _span(frm, to):
    return f"{_y(frm)} to {_y(to, ce=frm < 0 <= to)}"


def _signed(v):
    return ("+" if v > 0 else "") + fmt_num(v)


def _unit(units):
    u = (units or "").replace(" anomaly", "")
    return "" if u in ("", "dimensionless") else " " + u


def bandt_queries():
    """Band T queries: the fixtures that carry a span, plus the Band T-only fixtures (F35 to F45)."""
    fx, _, _ = P.load_all()
    return [q for q in fx if q["body"].get("temporal")] + P.load_bandt()


def evaluate_query(q):
    b = q["body"]
    span = b.get("temporal")
    if not span:
        return []
    frm, to = span["from_year"], span["to_year"]
    sc = b["scope"]
    base = dict(qid=q["id"], scope=sc["type"], level=q["params"]["level"], n_units=sc.get("n_units"), method=None, status=None)
    out = []

    def rec(i, item, applies, reason=None, text=None, stat=None):
        out.append(dict(base, id=i, variable=item, applies=applies, reason=reason, text=text, stat=stat))

    rows = [r for r in b["rows"] if r["band"] == "T"]
    lmr = {v: sorted([r for r in rows if r["variable"] == v], key=lambda r: r["year"]) for v in LMR_NAMES}
    hyde = {v: sorted([r for r in rows if r["variable"] == v], key=lambda r: r["epoch_year"]) for v in HYDE_NAMES}
    ev = sorted([r for r in rows if r["variable"] == "evolv2k_vssi"], key=lambda r: r["year"])
    cav = b.get("caveats") or {}

    # LMR: per variable
    for v, name in LMR_NAMES.items():
        rs = lmr[v]
        if not rs:
            rec("BT-01", v, False, "no_lmr_rows")
            rec("BT-02", v, False, "no_lmr_rows")
            continue
        vals = [r["representative_raw"] for r in rs]
        u = _unit(rs[0].get("units"))
        if len(rs) == 1:
            t = f"{name}: in {_y(rs[0]['year'])} the anomaly is {_signed(vals[0])}{u}, against the 850-1850 CE reference."
        else:
            lo, hi = min(rs, key=lambda r: r["representative_raw"]), max(rs, key=lambda r: r["representative_raw"])
            t = (f"{name}, {_span(rs[0]['year'], rs[-1]['year'])}: the yearly anomaly averages {_signed(sum(vals) / len(vals))}{u}, "
                 f"lowest {_signed(lo['representative_raw'])}{u} in {_y(lo['year'])}, highest {_signed(hi['representative_raw'])}{u} in {_y(hi['year'])}, "
                 "against the 850-1850 CE reference.")
        rec("BT-01", v, True, text=t, stat=sum(vals) / len(vals))
        mid = rs[len(rs) // 2]
        d = (mid.get("detail") or {}).get("distribution") or {}
        if (d.get("n_units") or 0) < 2:
            rec("BT-02", v, False, "one_cell")
        else:
            if _signed(d["min"]) == _signed(d["max"]):
                t2 = f"{name}: in {_y(mid['year'])}, the {d['n_units']} grid cells agree: {_signed(d['min'])}{u}."
            else:
                t2 = f"{name}: in {_y(mid['year'])}, the values across the {d['n_units']} grid cells range from {_signed(d['min'])} to {_signed(d['max'])}{u}."
            rec("BT-02", v, True, text=t2, stat=d["max"] - d["min"])

    # LMR: footprint and coverage
    any_lmr = [r for v in lmr.values() for r in v]
    if not any_lmr:
        rec("BT-03", "(query)", False, "no_lmr_rows")
    else:
        d = (any_lmr[0].get("detail") or {}).get("distribution") or {}
        n, low = d.get("n_units"), d.get("low_resolution")
        rec("BT-03", "(query)", True, text=f"The footprint touches {n} LMR grid cells (each 2 degrees wide), so each yearly value is built from {n} cells"
                                          + ("; the engine marks this low resolution." if low else "."), stat=n)
    years = sorted({r["year"] for r in any_lmr})
    if not years:
        if to < LMR_FIRST or frm > LMR_LAST:
            rec("BT-04", "(query)", True, text=f"The span lies outside the LMR record (0 to 1998 CE), so there are no LMR values.", stat=0)
        else:
            rec("BT-04", "(query)", False, "no_rows_inside_record")
    elif years[0] > frm or years[-1] < to:
        rec("BT-04", "(query)", True, text=f"LMR covers {_span(years[0], years[-1])} of the span {_span(frm, to)} (the record runs 0 to 1998 CE); there are no values for the rest.",
            stat=len(years) / (to - frm + 1))
    else:
        rec("BT-04", "(query)", False, "fully_covered")

    # HYDE
    epochs = sorted({r["epoch_year"] for v in hyde.values() for r in v})
    if not epochs:
        for i in ("BT-05", "BT-07", "BT-08"):
            rec(i, "(query)", False, "no_hyde_rows")
        for v in HYDE_NAMES:
            rec("BT-06", v, False, "no_hyde_rows")
    else:
        if len(epochs) == 1:
            vals = {v: hyde[v][0]["representative_raw"] for v in HYDE_NAMES if hyde[v]}
            rec("BT-05", "(query)", True, text=f"HYDE land use ({_y(epochs[0])} epoch): " + ", ".join(f"{HYDE_NAMES[v]} {fmt_num(x)} km²" for v, x in vals.items()) + ".",
                stat=sum(vals.values()))
        else:
            rec("BT-05", "(query)", False, "several_epochs")
        for v, name in HYDE_NAMES.items():
            rs = hyde[v]
            if len(rs) < 2:
                rec("BT-06", v, False, "single_epoch")
            else:
                a, z = rs[0], rs[-1]
                ch = z["representative_raw"] - a["representative_raw"]
                pct = f" ({ch / a['representative_raw']:+.0%})" if a["representative_raw"] > 0 else ""
                rec("BT-06", v, True, text=f"HYDE {name}: {fmt_num(a['representative_raw'])} km² in {_y(a['epoch_year'])}, {fmt_num(z['representative_raw'])} km² in "
                                           f"{_y(z['epoch_year'])}, a change of {_signed(ch)} km²{pct} across {len(rs)} epochs.",
                    stat=(ch / a["representative_raw"] if a["representative_raw"] > 0 else None))
        if "hyde_nearest_year" in cav:
            e = epochs[0]
            d = frm - e if e < frm else e - to
            rec("BT-07", "(query)", True, text=f"No HYDE epoch falls within the span; the nearest, the {_y(e)} epoch, is {d} years {'before' if e < frm else 'after'} it.", stat=d)
        else:
            rec("BT-07", "(query)", False, "epoch_inside_span")
        if "hyde_caveat" in cav:
            rec("BT-08", "(query)", True, text=f"HYDE 1950 epoch: {cav['hyde_caveat']}")
        else:
            rec("BT-08", "(query)", False, "no_caveat")

    # eVolv2k
    if ev:
        big = max(ev, key=lambda r: r["representative_raw"])
        n = len(ev)
        k = big["year"] - frm
        timing = "in the first year of the span" if k == 0 else f"{k} year{'' if k == 1 else 's'} into the span"
        size = f"injected {fmt_num(big['representative_raw'])} Tg S of stratospheric sulfur"
        if frm == to:
            t = f"In {_y(frm)}, one volcanic event {size}."
        elif n == 1:
            t = f"One volcanic event in {_span(frm, to)}, in {_y(big['year'])}, {size} ({timing})."
        else:
            t = f"{n} volcanic events in {_span(frm, to)}: the largest, in {_y(big['year'])}, {size} ({timing})."
        rec("BT-09", "(query)", True, text=t, stat=big["representative_raw"])
        rec("BT-10", "(query)", False, "events_present")
    else:
        rec("BT-09", "(query)", False, "no_events")
        if to < EV_FIRST or frm > EV_LAST:
            t = "The span lies outside the eVolv2k record (491 BCE to 1890 CE)."
        elif frm < EV_FIRST or to > EV_LAST:
            t = f"No volcanic events are recorded in the covered part of the span {_span(frm, to)} (the eVolv2k record covers 491 BCE to 1890 CE)."
        else:
            t = f"No volcanic events are recorded in {_span(frm, to)}."
        rec("BT-10", "(query)", True, text=t, stat=0)
    return out


def inventory(queries):
    """One dict per Band T query: what each source carries (the evidence the family rests on)."""
    out = []
    for q in queries:
        b = q["body"]
        rows = [r for r in b["rows"] if r["band"] == "T"]
        lmr = [r for r in rows if r["variable"].startswith("lmr")]
        hy = [r for r in rows if r["variable"] == "hyde_cropland"]
        ev = [r for r in rows if r["variable"] == "evolv2k_vssi"]
        d = ((lmr[0].get("detail") or {}).get("distribution") or {}) if lmr else {}
        yrs = sorted({r["year"] for r in lmr})
        out.append(dict(qid=q["id"], scope=b["scope"]["type"], level=q["params"]["level"],
                        span=f"{b['temporal']['from_year']} to {b['temporal']['to_year']}",
                        lmr_years=(f"{yrs[0]}-{yrs[-1]} ({len(yrs)})" if yrs else "none"), lmr_cells=d.get("n_units"), low_res=d.get("low_resolution"),
                        hyde_epochs=len(hy), hyde_n_cells=((hy[0].get("detail") or {}).get("distribution") or {}).get("n_units") if hy else None,
                        events=len(ev), caveats=",".join(sorted(b.get("caveats") or {})), rows=len(rows), kb=round(q["bytes"] / 1024)))
    return out


def hyde_grazing_check(queries):
    """Does grazing land equal pasture plus rangeland at every epoch? Returns (epochs checked, equal within 0.5 km², worst difference)."""
    n = eq = 0
    worst = 0.0
    for q in queries:
        by = {}
        for r in q["body"]["rows"]:
            if r["band"] == "T" and r["variable"].startswith("hyde"):
                by.setdefault(r["epoch_year"], {})[r["variable"]] = r["representative_raw"]
        for e, d in by.items():
            if len(d) == 4:
                n += 1
                diff = abs(d["hyde_grazing"] - (d["hyde_pasture"] + d["hyde_rangeland"]))
                worst = max(worst, diff)
                eq += diff <= 0.5
    return n, eq, worst


def record_bounds(queries):
    """First and last year seen in LMR rows, in eVolv2k rows, and the HYDE epochs seen."""
    ly, ey, he = [], [], set()
    for q in queries:
        for r in q["body"]["rows"]:
            if r["band"] == "T":
                if r["variable"].startswith("lmr"):
                    ly.append(r["year"])
                elif r["variable"].startswith("evolv2k"):
                    ey.append((r["year"], r["representative_raw"]))
                elif r["variable"] == "hyde_cropland":
                    he.add(r["epoch_year"])
    return (min(ly), max(ly)), sorted(set(ey)), sorted(he)
