"""WO-02 Step 3, family 6: Categorical (a class label, or a mixture of classes, with no percentile).

Rules read class_mixture rows with status ok or low_coverage (no_data belongs to Empty cells; low coverage also gets EMP-05).
Mixture shares are normalised here by their own sum: the engine renormalises every categorical variable over the covered part
of the area except outlet_type, whose weights sum to the covered share of the whole circle (37 buffer rows, sea). Rules describe
and never judge (WO constraint 1). Two wordings rest on cutoffs and are swept in the notebook: how many classes to list (n) and
the concentrated or mixed label (modal share 0.85, the engine's provisional cutoff).
"""
from scripts.edop.dashboard import wo02_payloads as P

TOP_N = 3          # classes listed in CAT-03; swept in the notebook (residual after the top n)

STATEMENTS = [
    dict(id="CAT-01", name="The class (one basin)",
         inputs="representative_raw (modal class label), n_units, status",
         rule="One basin, class_mixture row with a class: state the class.",
         applies_to="single basin and one-basin buffer; class_mixture (10 variables); L6, L8",
         does_not_apply_when="several basins (CAT-02, CAT-03); status no_data (EMP-03)",
         template="{name}: {label}.",
         in_ui_today="yes: the modal class label",
         needs_new_data="no; some labels are the source's own and need a reader's note (biome has a class labelled 'N/A')"),
    dict(id="CAT-02", name="The most common class and its share (area)",
         inputs="mixture, modal_class_id, n_classes, status",
         rule="Several basins, status ok or low_coverage: state the largest class and its share of the area that has a recorded class (normalised); if one class only, say all of the area with a recorded class is that class (not 'the whole area': in a buffer with sea only part of the circle has a recorded class).",
         applies_to="buffer, polity; class_mixture; L6, L8",
         does_not_apply_when="one basin; status no_data",
         template="{name}: {label} is the most common class, covering {share} of the area with a recorded class. | {name}: all of the area with a recorded class is {label}.",
         in_ui_today="partly: the modal label with a share bar (cheat sheet 4.2)",
         needs_new_data="no"),
    dict(id="CAT-03", name="The mixture: top classes and the rest (area)",
         inputs="mixture (class_label, weight), n_classes",
         rule="Several basins, two or more classes: list the top three with their shares and give the share of the remaining classes. How many to list is a display choice; the residual after the top n is swept in the notebook.",
         applies_to="buffer, polity; class_mixture; L6, L8",
         does_not_apply_when="one basin; only one class (CAT-02 says so); status no_data",
         template="{name}: {label} {share}; {label} {share}; {label} {share}; {k} other classes {share}.",
         in_ui_today="no: only the modal class and its share are shown; the rest of the mixture is in the payload",
         needs_new_data="no"),
    dict(id="CAT-04", name="Concentrated or mixed (the engine's label) as wording",
         inputs="coherence (concentrated or mixed), modal share",
         rule="Several basins and two or more classes: echo the engine's label (with one class it adds nothing to CAT-02). Its cutoff (modal share 0.85) is provisional and swept in the notebook; where it flips the label is dropped and CAT-02's share carries the information.",
         applies_to="buffer, polity; class_mixture; L6, L8",
         does_not_apply_when="one basin; only one class; status no_data",
         template="{name}: the classes are {concentrated|mixed}.",
         in_ui_today="no: the Sandbox shows the modal share bar but no concentrated or mixed badge for categorical rows",
         needs_new_data="no"),
]


def _p(x):
    """Whole percent, with 'less than 1%' for a positive share that would round to 0%."""
    return "less than 1%" if 0 < x < 0.005 else f"{x:.0%}"


def _norm(mixture):
    tot = sum(m["weight"] for m in mixture)
    return [(m["class_label"], m["weight"] / tot) for m in mixture] if tot else []


def evaluate(ctx, row):
    res = {}

    def no(i, why):
        res[i] = dict(applies=False, reason=why, text=None, stat=None)

    def yes(i, text, stat=None):
        res[i] = dict(applies=True, reason=None, text=text, stat=stat)

    name = row.get("friendly_name") or row["variable"]
    single = ctx["n_units"] == 1
    d = row.get("detail") or {}
    mix = _norm(d.get("mixture") or [])
    if row["method"] != "class_mixture":
        base = f"method:{row['method']}"
    elif row["status"] not in ("ok", "low_coverage"):
        base = f"status:{row['status']}"
    elif not mix:
        base = "no_mixture"
    else:
        base = None

    if base:
        for i in ("CAT-01", "CAT-02", "CAT-03", "CAT-04"):
            no(i, base)
        return res
    label, top = mix[0]
    if single:
        yes("CAT-01", f"{name}: {label}.", top)
        for i in ("CAT-02", "CAT-03", "CAT-04"):
            no(i, "one_unit")
        return res
    no("CAT-01", "multi_unit")
    if len(mix) == 1:
        yes("CAT-02", f"{name}: all of the area with a recorded class is {label}.", top)
        no("CAT-03", "one_class")
    else:
        yes("CAT-02", f"{name}: {label} is the most common class, covering {_p(top)} of the area with a recorded class.", top)
        listed = mix[:TOP_N]
        rest = mix[TOP_N:]
        t = f"{name}: " + "; ".join(f"{l} {_p(w)}" for l, w in listed)
        if rest:
            r = sum(w for _, w in rest)
            t += f"; {len(rest)} other class{'es' if len(rest) != 1 else ''} {_p(r)}"
        yes("CAT-03", t + ".", sum(w for _, w in rest))
    coh = row.get("coherence")
    if len(mix) == 1:
        no("CAT-04", "one_class")
    elif coh not in ("concentrated", "mixed"):
        no("CAT-04", f"coherence:{coh}")
    else:
        yes("CAT-04", f"{name}: the classes are {coh}.", top)
    return res


def evaluate_query(q):
    out = []
    for ctx, row in P.ae_rows(q):
        if row["method"] != "class_mixture":
            continue
        for i, r in evaluate(ctx, row).items():
            out.append(dict(qid=ctx["qid"], scope=ctx["scope"], level=ctx["level"], n_units=ctx["n_units"],
                            variable=row["variable"], method=row["method"], status=row["status"],
                            coherence=row.get("coherence"), id=i, **r))
    return out


def mixture_checks(queries):
    """Counters over class_mixture rows with a mixture: weights sum to 1, concentration equals the sum of squared shares,
    classes labelled N/A, and the number of classes in multi-basin rows."""
    import collections
    c = collections.Counter()
    nclass = collections.Counter()
    for q in queries:
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            if r["method"] != "class_mixture" or r["status"] not in ("ok", "low_coverage") or not d.get("mixture"):
                continue
            w = [m["weight"] for m in d["mixture"]]
            c["rows"] += 1
            c["weights sum to 1" if abs(sum(w) - 1) < 1e-3 else f"weights do not sum to 1 ({r['variable']})"] += 1
            c["concentration = sum of squared shares"] += abs(sum(x * x for x in w) - d["concentration"]) < 2e-3
            c["sorted largest first"] += w == sorted(w, reverse=True)
            if any(m["class_label"] == "N/A" for m in d["mixture"]):
                c[f"an 'N/A' class ({r['variable']})"] += 1
            if ctx["scope"] != "single_basin":
                nclass[min(len(w), 6)] += 1
    return c, nclass


def residual_by_n(df_rows, ns=(1, 2, 3, 4, 5)):
    """For multi-basin class rows: list of (query id, weight-free) residual shares after the top n classes."""
    out = []
    for q in df_rows:
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            if (ctx["scope"] != "single_basin" and r["method"] == "class_mixture" and r["status"] in ("ok", "low_coverage")
                    and d.get("mixture")):
                mix = _norm(d["mixture"])
                out.append((ctx["qid"], r["variable"], len(mix), [sum(w for _, w in mix[n:]) for n in ns]))
    return out


def label_vs_normalised(queries, cut=0.85):
    """Counter of (variable, engine label, label implied by the normalised modal share) where the two disagree, over multi-basin rows."""
    import collections
    c = collections.Counter()
    for q in queries:
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            if (ctx["scope"] != "single_basin" and r["method"] == "class_mixture" and r["status"] in ("ok", "low_coverage")
                    and d.get("mixture") and r.get("coherence")):
                top = _norm(d["mixture"])[0][1]
                mine = "concentrated" if top >= cut else "mixed"
                if mine != r["coherence"]:
                    c[(r["variable"], r["coherence"], mine)] += 1
    return c
