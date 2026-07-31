"""Validation for scripts/cdop/distance_core.py -- WO8d's factored distance module."""
import numpy as np
import pandas as pd
import pytest

from scripts.cdop.distance_core import (
    LENSES, backdrop_z, pairwise_distance, cohesion,
    random_draw_cohesions, family_restricted_draw_cohesions, percentile_rank,
    displacement, random_draw_stats, displacement_percentile_rank, top_families, scan,
    VARIABLES, variable_percentiles,
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


# ---------------------------------------------------------------------------
# WO4 additions: displacement, random_draw_stats, top_families, scan
# ---------------------------------------------------------------------------

def test_displacement_zero_when_centered_on_backdrop():
    # Backdrop mean is the origin in z-space by construction; a "subset" that is the whole
    # backdrop has centroid == origin, so displacement == 0.
    rng = np.random.default_rng(10)
    Xz = rng.normal(0, 1, (500, 3))
    Xz -= Xz.mean(axis=0)   # exact zero-mean, avoiding sampling-noise nonzero centroid
    assert displacement(Xz) == pytest.approx(0.0, abs=1e-9)


def test_displacement_detects_offset_group():
    # A subset shifted away from the origin should have nonzero, larger displacement than an
    # unshifted subset of the same size/spread.
    rng = np.random.default_rng(11)
    centered = rng.normal(0, 1, (30, 3))
    shifted = rng.normal(0, 1, (30, 3)) + np.array([5.0, 0.0, 0.0])
    assert displacement(centered) < displacement(shifted)
    assert displacement(shifted) == pytest.approx(5.0, abs=0.5)


def test_random_draw_stats_reproduces_random_draw_cohesions():
    # The whole point of duplicating the draw loop rather than refactoring: same seed/k/n_draws
    # against the same backdrop must give byte-identical cohesion values to the original WO8d
    # function, so WO8d's own numbers still reproduce through the new path.
    rng = np.random.default_rng(12)
    Xz = rng.normal(0, 1, (300, 4))
    coh_only = random_draw_cohesions(Xz, k=25, n_draws=500, seed=7)
    coh_joint, disp_joint = random_draw_stats(Xz, k=25, n_draws=500, seed=7)
    np.testing.assert_array_equal(coh_only, coh_joint)
    assert disp_joint.shape == (500,)
    assert np.all(disp_joint >= 0)


def test_displacement_percentile_rank_extremes():
    dist = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    # value below every draw -> more displaced than none of them
    assert displacement_percentile_rank(0.5, dist) == pytest.approx(0.0)
    # value above every draw -> more displaced than all of them
    assert displacement_percentile_rank(10.0, dist) == pytest.approx(1.0)


def test_top_families_dominant_case():
    # WO8d's own shape: one family clearly dominant, two smaller ones, no threshold needed.
    ids = pd.Series(["atla1278"] * 15 + ["nilo1247"] * 4 + ["sino1245"] * 3 + [None] * 2)
    out = top_families(ids, top_n=3)
    assert out["n_total"] == 24
    assert out["n_unresolved"] == 2
    assert out["top_families"][0] == {"family_id": "atla1278", "n": 15, "share": pytest.approx(15 / 24)}
    assert [f["family_id"] for f in out["top_families"]] == ["atla1278", "nilo1247", "sino1245"]


def test_top_families_no_dominant_case():
    # WO8d's Siberian-trio shape: several small, unrelated families, none dominant -- must not
    # need special-casing to report correctly (this is exactly the pattern a single-"dominant
    # family" framing would miss).
    ids = pd.Series(["chuk1273", "yaku1245", "nenet1249"])
    out = top_families(ids, top_n=3)
    assert out["n_total"] == 3
    assert out["n_unresolved"] == 0
    shares = {f["family_id"]: f["share"] for f in out["top_families"]}
    assert shares == {"chuk1273": pytest.approx(1 / 3), "yaku1245": pytest.approx(1 / 3),
                       "nenet1249": pytest.approx(1 / 3)}


def test_top_families_fewer_than_top_n():
    ids = pd.Series(["a", "a", "b"])
    out = top_families(ids, top_n=3)
    assert len(out["top_families"]) == 2   # only 2 distinct families exist; no padding


def test_top_families_other_bucket_pools_the_remainder():
    # 24 total: top-3 by count are a(6)/b(5)/c(4) = 15; the other 3 distinct families (d,e,f,
    # 1 each) should pool into "other" = 3, not vanish or get silently folded into the top-3.
    ids = pd.Series(["a"] * 6 + ["b"] * 5 + ["c"] * 4 + ["d", "e", "f"] + [None] * 6)
    out = top_families(ids, top_n=3)
    assert out["n_total"] == 24
    assert out["n_unresolved"] == 6
    assert [f["family_id"] for f in out["top_families"]] == ["a", "b", "c"]
    assert out["other"]["n"] == 3
    assert out["other"]["share"] == pytest.approx(3 / 24)


def test_top_families_soc_ids_included_when_requested():
    ids = pd.Series(["a", "a", "b", None])
    socs = pd.Series(["S1", "S2", "S3", "S4"])
    out = top_families(ids, top_n=3, soc_ids=socs)
    fam_a = next(f for f in out["top_families"] if f["family_id"] == "a")
    assert sorted(fam_a["soc_ids"]) == ["S1", "S2"]
    assert out["unresolved"]["soc_ids"] == ["S4"]
    assert out["other"]["soc_ids"] == []


def test_top_families_soc_ids_omitted_when_not_requested():
    ids = pd.Series(["a", "a", "b"])
    out = top_families(ids, top_n=3)
    assert "soc_ids" not in out["top_families"][0]
    assert "soc_ids" not in out["other"]
    assert "soc_ids" not in out["unresolved"]


def _synthetic_substrate(rng, n=400):
    df = pd.DataFrame({
        "soc_id": [f"S{i}" for i in range(n)],
        "ari_ix_sav": rng.uniform(0.1, 2.0, n),
        "temperature_annual": rng.normal(20, 8, n),
        "tmp_seas_amp": rng.normal(10, 4, n),
        "relief_range_m": rng.normal(200, 150, n).clip(min=0),
        "landform_position": rng.uniform(0, 1, n),
        "family_id": rng.choice(["fam0", "fam1", "fam2", "fam3", None], size=n,
                                 p=[0.3, 0.2, 0.2, 0.2, 0.1]),
        "trait": rng.choice(["X", "Y"], size=n, p=[0.1, 0.9]),
    })
    return df


def test_scan_shape_and_keys():
    rng = np.random.default_rng(20)
    df = _synthetic_substrate(rng)
    out = scan(df, trait_col="trait", value="X", n_draws=200, seed=0)
    assert out["trait_col"] == "trait"
    assert out["value"] == "X"
    assert out["n_focus_input"] == int((df["trait"] == "X").sum())
    assert set(out["lenses"].keys()) == set(LENSES.keys())
    for lens, res in out["lenses"].items():
        assert "obs_cohesion" in res and "obs_displacement" in res
        assert "pct_tighter_than_random" in res and "displacement_pct_rank" in res
        assert res["n_focus"] == out["n_focus_input"]   # no NaNs planted in this lens's columns
    assert out["composition"]["n_total"] == out["n_focus_input"]


def test_scan_derives_ari_log_when_missing():
    rng = np.random.default_rng(21)
    df = _synthetic_substrate(rng)
    assert "ari_log" not in df.columns
    out = scan(df, trait_col="trait", value="X", n_draws=50, seed=0)
    assert "water" in out["lenses"] and out["lenses"]["water"]["n_focus"] > 0


def test_scan_focus_mask_survives_lens_specific_row_drops():
    # Regression test for a real bug caught in WO4 Step 1 validation (Karl's notebook run,
    # 2026-07-30): scan() originally computed the focus mask once against `sub`'s original index
    # and reindexed it onto `backdrop_z`'s post-dropna, reset_index(drop=True) index -- which
    # coincidentally lines up when a lens drops zero rows, but silently selects the WRONG rows
    # once a lens drops rows that are NOT all at the end of the frame. This planted case mirrors
    # that exactly: NaNs scattered through the middle of the frame (not trailing), on a
    # terrain-only column, so a naive reindex-based mask would misalign for that lens while
    # `water`/`thermal` (unaffected columns) stay fine.
    rng = np.random.default_rng(30)
    n = 200
    df = _synthetic_substrate(rng, n=n)
    # Scatter NaNs through the middle third of the frame, not the tail -- the exact condition
    # that let the original bug slip past a same-size/no-shift check.
    nan_idx = np.arange(60, 90)
    df.loc[nan_idx, "landform_position"] = np.nan

    # Focus group deliberately straddles the NaN block on both sides.
    focus_idx = [50, 55, 65, 75, 85, 95, 105]   # 65/75/85 fall inside the dropped block
    df.loc[:, "trait"] = "OTHER"
    df.loc[focus_idx, "trait"] = "FOCUS"

    out = scan(df, trait_col="trait", value="FOCUS", n_draws=100, seed=0)

    # Ground truth, computed directly against the terrain lens's own post-dropna frame (the same
    # computation `scan()` must now perform internally).
    ok, Xz = backdrop_z(df, "terrain")
    true_fmask = (ok["trait"] == "FOCUS").to_numpy()
    expected_n_focus = int(true_fmask.sum())   # 4: three of the 7 focus rows sit in the dropped block
    expected_cohesion = cohesion(Xz[true_fmask])

    assert out["lenses"]["terrain"]["n_focus"] == expected_n_focus
    assert out["lenses"]["terrain"]["obs_cohesion"] == pytest.approx(expected_cohesion)
    # A lens untouched by the NaNs should see all 7 focus rows, unaffected.
    assert out["lenses"]["water"]["n_focus"] == 7


def test_scan_detects_planted_tight_displaced_group():
    # A group planted tight AND displaced on the 'thermal' lens should read as unusual there
    # (high pct_tighter_than_random, high displacement_pct_rank) but not necessarily on 'water'
    # (untouched, should look ordinary).
    rng = np.random.default_rng(22)
    df = _synthetic_substrate(rng, n=600)
    planted = df.sample(n=25, random_state=1).index
    df.loc[planted, "trait"] = "PLANTED"
    df.loc[planted, "temperature_annual"] = rng.normal(45, 0.5, len(planted))  # hot, tight
    df.loc[planted, "tmp_seas_amp"] = rng.normal(0.5, 0.1, len(planted))

    out = scan(df, trait_col="trait", value="PLANTED", n_draws=1000, seed=0)
    thermal = out["lenses"]["thermal"]
    assert thermal["pct_tighter_than_random"] > 95
    assert thermal["displacement_pct_rank"] > 95


# ---------------------------------------------------------------------------
# variable_percentiles() -- the WO4 meter-bar replacement for the lens scan
# ---------------------------------------------------------------------------

def test_variable_percentiles_shape_and_keys():
    rng = np.random.default_rng(30)
    df = _synthetic_substrate(rng)
    out = variable_percentiles(df, trait_col="trait", value="X")
    assert out["n_focus_input"] == int((df["trait"] == "X").sum())
    assert set(out["variables"].keys()) == set(VARIABLES.keys())
    for key, res in out["variables"].items():
        assert res["n_focus"] > 0
        assert 0 <= res["percentile"] <= 100
        assert res["direction"] in (res["pole_low"], res["pole_high"])
        assert res["qualifier"] in ("typical", "somewhat", "very")


def test_variable_percentiles_derives_ari_log_when_missing():
    rng = np.random.default_rng(31)
    df = _synthetic_substrate(rng)
    assert "ari_log" not in df.columns
    out = variable_percentiles(df, trait_col="trait", value="X")
    assert out["variables"]["aridity"]["n_focus"] > 0


def test_variable_percentiles_direction_and_qualifier_on_planted_extreme():
    # A group planted at the very top of the temperature range should read "very" + "Warm",
    # not just "somewhat" -- checks the qualifier bucketing and pole direction together rather
    # than each in isolation with hand-picked percentiles.
    rng = np.random.default_rng(32)
    df = _synthetic_substrate(rng, n=500)
    planted = df.sample(n=20, random_state=2).index
    df.loc[planted, "trait"] = "HOT"
    df.loc[planted, "temperature_annual"] = 200.0   # far past the backdrop's own range

    out = variable_percentiles(df, trait_col="trait", value="HOT")
    temp = out["variables"]["temperature"]
    assert temp["percentile"] > 95
    assert temp["direction"] == "Warm"
    assert temp["qualifier"] == "very"


def test_variable_percentiles_typical_group_reads_typical():
    # A group that's just a random subset of the backdrop (no plant) should land close to the
    # 50th percentile and read "typical" on every variable -- the Otiose-shaped case.
    rng = np.random.default_rng(33)
    df = _synthetic_substrate(rng, n=2000)
    df["trait"] = "Y"
    subset_idx = df.sample(n=400, random_state=3).index
    df.loc[subset_idx, "trait"] = "TYPICAL_SAMPLE"

    out = variable_percentiles(df, trait_col="trait", value="TYPICAL_SAMPLE")
    for key, res in out["variables"].items():
        assert 35 <= res["percentile"] <= 65, f"{key} landed at {res['percentile']}, not typical"
        assert res["qualifier"] == "typical"


def test_variable_percentiles_missing_column_data_reports_zero_not_error():
    rng = np.random.default_rng(34)
    df = _synthetic_substrate(rng)
    df["landform_position"] = np.nan   # whole column missing -- no complete-case overlap at all
    out = variable_percentiles(df, trait_col="trait", value="X")
    assert out["variables"]["landform"]["n_focus"] == 0
    assert out["variables"]["aridity"]["n_focus"] > 0   # unaffected variables still compute
