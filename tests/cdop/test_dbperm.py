"""Validation for scripts/cdop/dbperm.py — no skbio needed; checks against closed-form F and the
Anderson sum-of-squared-distances identity, plus structural permutation properties."""
import numpy as np
import pytest
from scipy import stats

from scripts.cdop.dbperm import permanova, adonis_term, dbrda_trend, permdisp, gower_G


def _euclid(X):
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    G = X @ X.T
    d2 = np.diag(G)[:, None] + np.diag(G)[None, :] - 2 * G
    return np.sqrt(np.clip(d2, 0, None))


def _anderson_oneway_F(D, groups):
    """PERMANOVA pseudo-F via Anderson's sum-of-squared-distances identity (independent derivation)."""
    groups = np.asarray(groups)
    n = len(groups)
    labs = list(dict.fromkeys(groups.tolist()))
    a = len(labs)
    ss_total = (D[np.triu_indices(n, 1)] ** 2).sum() / n
    ss_within = 0.0
    for g in labs:
        idx = np.where(groups == g)[0]
        ng = len(idx)
        sub = D[np.ix_(idx, idx)]
        ss_within += (sub[np.triu_indices(ng, 1)] ** 2).sum() / ng
    ss_among = ss_total - ss_within
    return (ss_among / (a - 1)) / (ss_within / (n - a))


def _clustered(rng, sizes, sep, dim=3, spread=1.0):
    X, g = [], []
    for k, m in enumerate(sizes):
        X.append(rng.normal(0, spread, (m, dim)) + np.array([sep * k] + [0] * (dim - 1)))
        g += [f"g{k}"] * m
    return np.vstack(X), np.array(g)


# ── the stat itself ──────────────────────────────────────────────────────────────────────────
def test_permanova_F_matches_anderson_identity():
    rng = np.random.default_rng(1)
    X, g = _clustered(rng, [20, 25, 15], sep=0.8)
    D = _euclid(X)
    F = permanova(D, g, n_perm=49, seed=0).F
    assert F == pytest.approx(_anderson_oneway_F(D, g), rel=1e-9)


def test_permanova_euclid_1d_equals_oneway_anova():
    rng = np.random.default_rng(2)
    y = np.concatenate([rng.normal(0, 1, 20), rng.normal(1.2, 1, 22), rng.normal(-0.6, 1, 18)])
    g = np.array(["a"] * 20 + ["b"] * 22 + ["c"] * 18)
    F_pm = permanova(_euclid(y), g, n_perm=49, seed=0).F
    F_anova = stats.f_oneway(y[g == "a"], y[g == "b"], y[g == "c"]).statistic
    assert F_pm == pytest.approx(F_anova, rel=1e-9)


def test_dbrda_trend_equals_regression_F():
    rng = np.random.default_rng(3)
    score = np.arange(60, dtype=float)
    y = 0.05 * score + rng.normal(0, 1, 60)
    res = dbrda_trend(_euclid(y), score, n_perm=49, seed=0)
    r = stats.linregress(score, y).rvalue
    F_reg = r ** 2 * (60 - 2) / (1 - r ** 2)
    assert res.df1 == 1
    assert res.F == pytest.approx(F_reg, rel=1e-9)


def test_partial_with_no_covars_equals_marginal():
    rng = np.random.default_rng(4)
    X, g = _clustered(rng, [15, 15, 15], sep=0.7)
    D = _euclid(X)
    assert adonis_term(D, g, covars=None, n_perm=49, seed=0).F == pytest.approx(
        permanova(D, g, n_perm=49, seed=0).F, rel=1e-9)


def test_gower_trace_is_total_ss():
    rng = np.random.default_rng(5)
    X, _ = _clustered(rng, [10, 10], sep=0.5)
    D = _euclid(X)
    n = len(D)
    assert np.trace(gower_G(D)) == pytest.approx((D[np.triu_indices(n, 1)] ** 2).sum() / n, rel=1e-9)


# ── permutation behaviour ─────────────────────────────────────────────────────────────────────
def test_restricted_blocks_equal_groups_gives_p_one():
    # If families coincide with the tested factor, no within-family permutation can move a label,
    # so every permuted F equals the observed -> p = 1. The Galton null at its degenerate limit.
    rng = np.random.default_rng(6)
    X, g = _clustered(rng, [12, 12, 12], sep=1.5)
    res = permanova(_euclid(X), g, blocks=g, n_perm=200, seed=0)
    assert res.p == pytest.approx(1.0)


def test_positive_control_small_p():
    rng = np.random.default_rng(7)
    X, g = _clustered(rng, [25, 25, 25], sep=3.0)   # well separated
    assert permanova(_euclid(X), g, n_perm=499, seed=0).p <= 0.01


def test_null_pvalue_is_uniformish():
    # No group effect -> mean p over many datasets should sit near 0.5.
    ps = []
    for s in range(40):
        rng = np.random.default_rng(100 + s)
        X = rng.normal(0, 1, (45, 3))
        g = np.array(["a", "b", "c"] * 15)
        ps.append(permanova(_euclid(X), g, n_perm=199, seed=s).p)
    assert 0.35 <= np.mean(ps) <= 0.65


# ── PERMDISP ───────────────────────────────────────────────────────────────────────────────────
def test_permdisp_flags_unequal_dispersion():
    rng = np.random.default_rng(8)
    A = rng.normal(0, 0.3, (30, 3))          # tight
    B = rng.normal(0, 2.0, (30, 3))          # spread, same centroid
    X = np.vstack([A, B]); g = np.array(["a"] * 30 + ["b"] * 30)
    assert permdisp(_euclid(X), g, n_perm=499, seed=0).p <= 0.02


def test_permdisp_equal_dispersion_not_significant_on_average():
    ps = []
    for s in range(30):
        rng = np.random.default_rng(200 + s)
        X = rng.normal(0, 1, (40, 3)); g = np.array(["a", "b"] * 20)
        ps.append(permdisp(_euclid(X), g, n_perm=199, seed=s).p)
    assert 0.3 <= np.mean(ps) <= 0.7


# ── return_null (WO8c effect-size floor) ─────────────────────────────────────────────────────
def test_return_null_default_false_matches_prior_behaviour():
    # return_null omitted must reproduce the exact pre-existing return shape and values.
    rng = np.random.default_rng(9)
    X, g = _clustered(rng, [20, 25, 15], sep=0.8)
    D = _euclid(X)
    res_plain = permanova(D, g, n_perm=49, seed=0)
    res_explicit = permanova(D, g, n_perm=49, seed=0, return_null=False)
    assert not isinstance(res_plain, tuple)
    assert res_plain == res_explicit


def test_return_null_shape_and_range():
    # Permutation draws are random relabellings, not guaranteed to include the identity, so the
    # observed R2 need not appear in the null array -- check shape and a sane, finite range instead.
    rng = np.random.default_rng(10)
    X, g = _clustered(rng, [20, 25, 15], sep=0.8)
    D = _euclid(X)
    res, null_R2 = permanova(D, g, n_perm=199, seed=0, return_null=True)
    assert null_R2.shape == (199,)
    assert np.all(np.isfinite(null_R2))
    assert np.all(null_R2 >= -1e-9)


def test_return_null_separates_signal_from_noise():
    # A well-separated effect's observed R2 should clear its own null's 95th percentile;
    # a shuffled (no-effect) version of the same data should not.
    rng = np.random.default_rng(11)
    X, g = _clustered(rng, [25, 25, 25], sep=3.0, spread=0.5)
    D = _euclid(X)
    res, null_R2 = permanova(D, g, n_perm=499, seed=0, return_null=True)
    floor = np.percentile(null_R2, 95)
    assert res.R2 > floor

    g_shuffled = rng.permutation(g)
    res0, null_R2_0 = permanova(D, g_shuffled, n_perm=499, seed=1, return_null=True)
    floor0 = np.percentile(null_R2_0, 95)
    assert res0.R2 <= floor0


def test_return_null_propagates_through_adonis_and_dbrda():
    rng = np.random.default_rng(12)
    X, g = _clustered(rng, [15, 15, 15], sep=1.0)
    D = _euclid(X)
    res_a, null_a = adonis_term(D, g, n_perm=49, seed=0, return_null=True)
    assert null_a.shape == (49,)

    score = np.arange(45, dtype=float)
    y = 0.05 * score + rng.normal(0, 1, 45)
    res_t, null_t = dbrda_trend(_euclid(y), score, n_perm=49, seed=0, return_null=True)
    assert null_t.shape == (49,)
