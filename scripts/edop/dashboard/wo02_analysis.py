"""WO-02 Step 3: generic analysis over a family's rules (any module exposing STATEMENTS and evaluate_query).

Fixtures are reported as counts (they are chosen conditions, not a sample). The population sample is reported
weighted to the world by climate-zone size (wo02_payloads.population_weights) and unweighted.
"""
import numpy as np
import pandas as pd
from scripts.edop.dashboard import wo02_payloads as P

KIND = {"s": "single L6", "b": "buffer L6", "t": "single L8"}


def apply_fixtures(fx, rules, **kw):
    return pd.DataFrame([r for q in fx for r in rules.evaluate_query(q, **kw)])


def fixture_table(df):
    res = np.where(df.applies, "applied", "not_applicable")
    t = df.assign(res=res).groupby(["id", "scope", "res"]).size().unstack("res", fill_value=0)
    return t.reindex(columns=["applied", "not_applicable"], fill_value=0)


def reason_table(df):
    return df[~df.applies].groupby(["id", "reason"]).size()


def apply_population(pop, weights, rules, **kw):
    out = []
    for q in pop:
        for r in rules.evaluate_query(q, **kw):
            r["w"] = weights[q["id"]]
            r["kind"] = KIND[q["kind"]]
            out.append(r)
    return pd.DataFrame(out)


def rates(df):
    """Weighted share of all Band A-E rows to which each statement applies, by statement and query kind."""
    d = df.assign(wa=df.w * df.applies)
    return (d.groupby(["id", "kind"]).wa.sum() / d.groupby(["id", "kind"]).w.sum()).unstack("kind")


def unweighted_rates(df):
    return df.groupby(["id", "kind"]).applies.mean().unstack("kind")


def stat_quantiles(df, ids, qs=(0.1, 0.25, 0.5, 0.75, 0.9)):
    rows = []
    for (sid, kind), g in df[df.applies & df.id.isin(ids)].groupby(["id", "kind"]):
        v = g.stat.astype(float)
        ok = v.notna()
        rows.append(dict(id=sid, kind=kind, n=int(ok.sum()), **{f"p{int(q * 100)}": P.wquantile(v[ok], g.w[ok], q) for q in qs}))
    return pd.DataFrame(rows)


def cutoff_sweep(df, sid, cuts):
    """For a statement whose wording depends on `stat >= cutoff`: weighted share at each cutoff, and the share
    of applicable rows whose wording changes somewhere between the lowest and the highest cutoff."""
    out = []
    for kind, g in df[(df.id == sid) & df.applies].groupby("kind"):
        v, w = g.stat.astype(float), g.w
        tot = w.sum()
        row = dict(kind=kind, n=len(g))
        for c in cuts:
            row[f">= {c}"] = float((w * (v >= c)).sum() / tot)
        row["flips"] = float((w * ((v >= cuts[0]) & (v < cuts[-1]))).sum() / tot)
        out.append(row)
    return pd.DataFrame(out)


def flipping_variables(df, sid, lo, hi, top=8):
    g = df[(df.id == sid) & df.applies]
    v = g.stat.astype(float)
    return g[(v >= lo) & (v < hi)].variable.value_counts().head(top)
