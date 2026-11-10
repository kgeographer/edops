"""WO-02 Distribution family: how much narrower is a buffer's middle 80% than a random draw of basins would give?

For each eligible buffer row (5+ basins, status ok, not suppressed, variable not zero-aware) the observed width p90 - p10 is
compared with 300 simulated draws of the same number of basins, with percentiles drawn uniformly on 0-100 and equal weights.
Assumptions: percentiles of a non-zero-aware variable are uniform by construction; the engine weights basins by area, which
is not in the payload, so equal weights are used. Seeded; run from the repo root: python -m scripts.edop.dashboard.wo02_autocorr_baseline
"""
import numpy as np
from scripts.edop.dashboard import wo02_payloads as P, wo02_rules_position as R

SEED, DRAWS = 20261031, 300


def sim_widths(k, rng):
    s = np.sort(rng.uniform(0, 100, size=(DRAWS, k)), axis=1)
    x = (np.arange(k) + 0.5) / k                       # same midpoint interpolation as the engine's weighted quantile
    p = lambda q: np.array([np.interp(q, x, row) for row in s])
    return p(0.9) - p(0.1)


def main():
    fx, pop, _ = P.load_all()
    W = P.population_weights(pop)
    rng = np.random.default_rng(SEED)
    rows = []   # (weight, k, observed width)
    for q in pop:
        if q["kind"] != "b":
            continue
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            zf = P.zero_fraction(r["variable"], ctx["level"])
            if (r["method"] == "area_weighted" and r["status"] == "ok" and not r.get("score_suppressed")
                    and (ctx["n_units"] or 0) >= 5 and d.get("p10") is not None and zf is not None and zf < R.ZERO_AWARE_THRESHOLD):
                rows.append((W[q["id"]], ctx["n_units"], d["p90"] - d["p10"]))
    w = np.array([x[0] for x in rows]); k = np.array([x[1] for x in rows]); obs = np.array([x[2] for x in rows])
    rank = np.zeros(len(rows)); sim_med = np.zeros(len(rows)); sim_p05 = np.zeros(len(rows))
    cache = {}
    for kk in sorted(set(k)):
        cache[kk] = sim_widths(int(kk), rng)
    for i, kk in enumerate(k):
        sw = cache[kk]
        rank[i] = (sw <= obs[i]).mean()            # share of random draws at least as narrow as the observed row
        sim_med[i], sim_p05[i] = np.median(sw), np.percentile(sw, 5)
    wq = lambda v, q: P.wquantile(v, w, q)
    print(f"eligible buffer rows: {len(rows)} (basins per buffer {int(k.min())} to {int(k.max())}, weighted median {int(wq(k, 0.5))})")
    print("width of the middle 80% (percentile points), weighted:")
    print("   observed            p10 %.1f  p25 %.1f  median %.1f  p75 %.1f  p90 %.1f" % tuple(wq(obs, q) for q in (.1, .25, .5, .75, .9)))
    print("   random draws (same k) median of each row's simulations, weighted quantiles of those medians:")
    print("                       p10 %.1f  p25 %.1f  median %.1f  p75 %.1f  p90 %.1f" % tuple(wq(sim_med, q) for q in (.1, .25, .5, .75, .9)))
    print("weighted median of observed / simulated median: %.2f" % (wq(obs, 0.5) / wq(sim_med, 0.5)))
    print("weighted median rank of the observed width within its own random draws (0 = narrower than all draws): %.3f" % wq(rank, 0.5))
    print("weighted share of rows narrower than the 5th percentile of random draws: %.1f%%" % (100 * (w * (obs < sim_p05)).sum() / w.sum()))
    print("weighted share of rows at least as wide as the median random draw: %.1f%%" % (100 * (w * (obs >= sim_med)).sum() / w.sum()))
    # lowest-to-highest range does not depend on the basin weights, so it removes the unequal-area confound
    rr = []
    for q in pop:
        if q["kind"] != "b":
            continue
        for ctx, r in P.ae_rows(q):
            dist = (r.get("detail") or {}).get("distribution") or {}
            zf = P.zero_fraction(r["variable"], ctx["level"])
            if (r["method"] == "area_weighted" and r["status"] == "ok" and not r.get("score_suppressed") and (ctx["n_units"] or 0) >= 5
                    and dist.get("min") is not None and zf is not None and zf < R.ZERO_AWARE_THRESHOLD):
                rr.append((W[q["id"]], ctx["n_units"], dist["max"] - dist["min"]))
    w2 = np.array([x[0] for x in rr]); k2 = np.array([x[1] for x in rr]); ob2 = np.array([x[2] for x in rr])
    cache2 = {}
    for kk in sorted(set(k2)):
        s2 = np.sort(rng.uniform(0, 100, size=(DRAWS, int(kk))), axis=1)
        cache2[kk] = s2[:, -1] - s2[:, 0]
    sm2 = np.array([np.median(cache2[kk]) for kk in k2]); sp2 = np.array([np.percentile(cache2[kk], 5) for kk in k2])
    wq2 = lambda v, q: P.wquantile(v, w2, q)
    print(f"lowest-to-highest range (no weights involved), {len(rr)} rows:")
    print("   observed            p10 %.1f  p25 %.1f  median %.1f  p75 %.1f  p90 %.1f" % tuple(wq2(ob2, q) for q in (.1, .25, .5, .75, .9)))
    print("   random draws median p10 %.1f  p25 %.1f  median %.1f  p75 %.1f  p90 %.1f" % tuple(wq2(sm2, q) for q in (.1, .25, .5, .75, .9)))
    print("   weighted median of observed / simulated median: %.2f | share of rows narrower than the 5th percentile of random draws: %.1f%%"
          % (wq2(ob2, 0.5) / wq2(sm2, 0.5), 100 * (w2 * (ob2 < sp2)).sum() / w2.sum()))
    # polities (fixtures): same comparison, one row per variable, equal weights across polities
    pol = []
    for q in fx:
        if q["body"]["scope"]["type"] != "polity":
            continue
        for ctx, r in P.ae_rows(q):
            d = r.get("detail") or {}
            zf = P.zero_fraction(r["variable"], ctx["level"])
            if (r["method"] == "area_weighted" and r["status"] == "ok" and not r.get("score_suppressed") and d.get("p10") is not None
                    and zf is not None and zf < R.ZERO_AWARE_THRESHOLD and ctx["n_units"] >= 5):
                pol.append((q["id"], ctx["n_units"], d["p90"] - d["p10"]))
    if pol:
        import collections
        by = collections.defaultdict(list)
        for qid, kk, wd in pol:
            by[(qid, kk)].append(wd)
        print("polity fixtures (basins; median observed width; median random-draw width):")
        for (qid, kk), v in sorted(by.items()):
            sw = sim_widths(int(kk), rng)
            print(f"   {qid} {kk:5d} basins  observed {np.median(v):5.1f}  random {np.median(sw):5.1f}  ({len(v)} variables)")


if __name__ == "__main__":
    main()
