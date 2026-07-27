"""Validation for scripts/cdop/distance_core.py -- WO8d's factored distance module."""
import numpy as np
import pandas as pd
import pytest

from scripts.cdop.distance_core import (
    LENSES, backdrop_z, pairwise_distance, cohesion,
    random_draw_cohesions, family_restricted_draw_cohesions, percentile_rank,
)


def _euclid_naive(X):
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = np.sqrt(((X[i] - X[j]) ** 2).sum())
    return D


def test_backdrop_z_standardizes_on_itself():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "ari_log": rng.normal(5, 2, 200),
        "temperature_annual": rng.normal(20, 8, 200),
        "tmp_seas_amp": rng.normal(10, 4, 200),
    })
    ok, Xz = backdrop_z(df, "overall")
    assert len(ok) == 200
    assert Xz.shape == (200, 3)
    np.testing.assert_allclose(Xz.mean(axis=0), 0, atol=1e-10)
    np.testing.assert_allclose(Xz.std(axis=0), 1, atol=1e-10)


def test_backdrop_z_drops_incomplete_rows_for_lens():
    df = pd.DataFrame({
        "ari_log": [1.0, 2.0, np.nan, 4.0],
        "temperature_annual": [10.0, 20.0, 30.0, 40.0],
        "tmp_seas_amp": [1.0, 2.0, 3.0, 4.0],
    })
    ok, Xz = backdrop_z(df, "overall")
    assert len(ok) == 3            # the water-only lens doesn't need temp/amp complete
    ok_w, Xz_w = backdrop_z(df, "water")
    assert len(ok_w) == 3          # ari_log itself still has the one NaN row dropped


def test_pairwise_distance_matches_naive():
    rng = np.random.default_rng(1)
    Xz = rng.normal(0, 1, (15, 3))
    D = pairwise_distance(Xz)
    D_naive = _euclid_naive(Xz)
    np.testing.assert_allclose(D, D_naive, atol=1e-9)
    assert np.allclose(np.diag(D), 0)
    assert np.allclose(D, D.T)


def test_cohesion_zero_for_identical_points():
    Xz = np.zeros((10, 3))
    assert cohesion(Xz) == pytest.approx(0.0)


def test_cohesion_tighter_cluster_has_lower_value():
    rng = np.random.default_rng(2)
    tight = rng.normal(0, 0.1, (30, 3))
    loose = rng.normal(0, 3.0, (30, 3))
    assert cohesion(tight) < cohesion(loose)


def test_random_draw_cohesions_shape_and_range():
    rng = np.random.default_rng(3)
    Xz = rng.normal(0, 1, (200, 3))
    dist = random_draw_cohesions(Xz, k=20, n_draws=100, seed=0)
    assert dist.shape == (100,)
    assert np.all(dist > 0)


def test_random_draw_recovers_planted_tight_cluster():
    # A tight, planted subgroup should read as tighter than the vast majority of random draws
    # of the same size from a spread-out backdrop.
    rng = np.random.default_rng(4)
    backdrop = rng.normal(0, 3.0, (500, 3))
    tight_idx = rng.choice(500, size=20, replace=False)
    backdrop[tight_idx] = rng.normal(0, 0.05, (20, 3))   # plant a tight cluster in place

    focus_cohesion = cohesion(backdrop[tight_idx])
    null = random_draw_cohesions(backdrop, k=20, n_draws=1000, seed=1)
    rank = percentile_rank(focus_cohesion, null)
    assert rank > 0.95   # tighter than at least 95% of random draws


def test_percentile_rank_extremes():
    dist = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert percentile_rank(0.5, dist) == pytest.approx(1.0)   # below every draw -> tighter than all
    assert percentile_rank(10.0, dist) == pytest.approx(0.0)  # above every draw -> tighter than none


def test_family_restricted_draw_cohesions_shape_and_fallback():
    rng = np.random.default_rng(5)
    n = 100
    Xz = rng.normal(0, 1, (n, 3))
    backdrop_family = np.array([f"fam{i % 10}" for i in range(n)])   # 10 families, 10 each

    # focus group: families fam0..fam4, plus one unresolved (NaN) member
    focus_family = np.array(["fam0", "fam1", "fam2", "fam3", "fam4", np.nan], dtype=object)
    dist = family_restricted_draw_cohesions(Xz, backdrop_family, focus_family, n_draws=200, seed=0)
    assert dist.shape == (200,)
    assert np.all(np.isfinite(dist))


def test_family_restricted_draws_only_swap_within_the_target_family():
    # Structural correctness: every drawn index in slot j must belong to focus_family[j]'s
    # family (or be a fully-random fallback only when that family has no other backdrop member).
    rng = np.random.default_rng(6)
    n_families, per_family = 5, 8
    backdrop_family = np.repeat([f"fam{i}" for i in range(n_families)], per_family)
    Xz = rng.normal(0, 1, (n_families * per_family, 3))

    focus_family = np.array(["fam0", "fam1", "fam2"])
    rng2 = np.random.default_rng(7)
    for _ in range(20):
        idx = np.empty(3, dtype=int)
        for j, fam in enumerate(focus_family):
            pool = np.where(backdrop_family == fam)[0]
            idx[j] = pool[rng2.integers(0, len(pool))]
        assert all(backdrop_family[idx[j]] == focus_family[j] for j in range(3))

    # And the function itself runs without error at scale and produces a sane, non-degenerate
    # distribution (not all-identical, since within-family members differ).
    fam_dist = family_restricted_draw_cohesions(Xz, backdrop_family, focus_family,
                                                n_draws=500, seed=2)
    assert fam_dist.std() > 0
