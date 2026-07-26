"""Distance-based linear models for WO8b — PERMANOVA / db-RDA / PERMDISP, hand-rolled.

No PERMANOVA library is installed (skbio/statsmodels absent), and none of them expresses the two
things WO8b hinges on — **restricted permutation within language family** (Galton control) and
**Freedman–Lane partial tests** (a term net of a covariate). So this is a small, tested numpy
implementation of the McArdle & Anderson (2001) distance-based framework.

Everything runs on the Gower double-centred matrix  G = -1/2 · J D^2 J  (J = I - 11'/N). For a
design X with hat H = X(X'X)^+X', the sum of squares attributable to the model is tr(H G) and the
residual is tr((I-H)G). A term X1 adjusted for X0 uses the projection difference H - H0
(idempotent, symmetric), so SS(X1|X0) = tr((H-H0) G).

Permutation:
  * `blocks` restricts shuffling to within-block (family) — the phylogenetic null.
  * Partial tests use Freedman–Lane: permute the reduced-model residuals R0 = (I-H0)G(I-H0).
    Because (H-H0)H0 = 0 and (I-H)H0 = 0, both the numerator tr((H-H0)·P R0 P') and the
    denominator tr((I-H)·P R0 P') depend only on the permuted residuals — the observed statistic
    is the P=identity case, so one code path serves both.

Public API:
  gower_G(D)                              -> centred G
  permanova(D, groups, ...)              -> one-factor pseudo-F, family-restricted p, R^2
  adonis_term(D, term, covars=..., ...)  -> `term` after `covars` (factor or ordinal); Freedman–Lane
  dbrda_trend(D, score, ...)             -> ordinal/monotonic 1-df test (adonis_term with ordinal term)
  permdisp(D, groups, ...)               -> betadisper: homogeneity of dispersions (Anderson 2006)

Validated in tests/cdop/test_dbperm.py against closed-form ANOVA/regression F and the Anderson
sum-of-squared-distances identity. Referenced by notebooks/cdop/wo8b_fixity_test.ipynb.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Union

import numpy as np
from scipy.linalg import orth

__all__ = ["gower_G", "permanova", "adonis_term", "dbrda_trend", "permdisp", "DBResult", "DispResult"]

_ArrayLike = Union[Sequence, np.ndarray]


@dataclass
class DBResult:
    F: float
    p: float
    R2: float
    df1: int
    df2: int
    n_perm: int
    n_used_perms: Optional[int] = None   # distinct permutations actually available (restricted case)


@dataclass
class DispResult:
    F: float
    p: float
    group_mean_dist: dict
    df1: int
    df2: int
    n_perm: int


# ── core linear algebra ──────────────────────────────────────────────────────────────────────
def gower_G(D: np.ndarray) -> np.ndarray:
    """Gower double-centred matrix G = -1/2 J D^2 J from a symmetric distance matrix D."""
    D = np.asarray(D, float)
    n = D.shape[0]
    A = -0.5 * (D ** 2)
    J = np.eye(n) - np.ones((n, n)) / n
    G = J @ A @ J
    return (G + G.T) / 2


def _design(x: _ArrayLike, ordinal: bool = False) -> np.ndarray:
    """Design block for one variable: centred numeric column if ordinal/continuous, else one-hot."""
    x = np.asarray(x)
    if ordinal or np.issubdtype(x.dtype, np.floating):
        col = x.astype(float)
        return (col - col.mean())[:, None]
    # categorical -> full one-hot (rank handled downstream by orth)
    levels = list(dict.fromkeys(x.tolist()))
    return np.column_stack([(x == lv).astype(float) for lv in levels])


def _stack(n: int, blocks_of_cols: Sequence[Optional[np.ndarray]]) -> np.ndarray:
    cols = [np.ones((n, 1))]
    for b in blocks_of_cols:
        if b is not None and b.size:
            cols.append(b)
    return np.hstack(cols)


def _hat(X: np.ndarray):
    """Orthonormal basis Q of col(X); returns (H = QQ', rank)."""
    Q = orth(X)                      # SVD-based, drops rank-deficient columns
    return Q @ Q.T, Q.shape[1]


def _perm_indices(n: int, blocks: Optional[np.ndarray], n_perm: int, rng) -> list:
    """`n_perm` index permutations. If blocks given, shuffle only within each block value."""
    if blocks is None:
        return [rng.permutation(n) for _ in range(n_perm)]
    blocks = np.asarray(blocks)
    groups = [np.where(blocks == b)[0] for b in dict.fromkeys(blocks.tolist())]
    out = []
    for _ in range(n_perm):
        pi = np.arange(n)
        for g in groups:
            if g.size > 1:
                pi[g] = g[rng.permutation(g.size)]
        out.append(pi)
    return out


def _n_restricted_perms(blocks: Optional[np.ndarray]) -> Optional[int]:
    """Order of the within-block permutation group (product of block-size factorials); None if free."""
    if blocks is None:
        return None
    from math import factorial
    total = 1
    for b in dict.fromkeys(np.asarray(blocks).tolist()):
        total *= factorial(int((np.asarray(blocks) == b).sum()))
        if total > 10 ** 12:
            return None
    return total


def _dblm(G: np.ndarray, Xfull: np.ndarray, X0: np.ndarray,
          blocks: Optional[np.ndarray], n_perm: int, seed: int) -> DBResult:
    """Test the extra columns of Xfull beyond X0 on centred G (Freedman–Lane residual permutation)."""
    n = G.shape[0]
    H, rank_f = _hat(Xfull)
    H0, rank_0 = _hat(X0)
    df1 = rank_f - rank_0
    df2 = n - rank_f
    if df1 <= 0 or df2 <= 0:
        raise ValueError(f"degenerate design (df1={df1}, df2={df2})")

    Hdiff = H - H0
    Imh = np.eye(n) - H
    R0 = (np.eye(n) - H0) @ G @ (np.eye(n) - H0)
    R0 = (R0 + R0.T) / 2
    ss_total = np.trace(G)

    def F_of(Rp: np.ndarray) -> float:
        num = np.einsum("ij,ij->", Hdiff, Rp)      # tr(Hdiff · Rp), both symmetric
        den = np.einsum("ij,ij->", Imh, Rp)
        return (num / df1) / (den / df2)

    F_obs = F_of(R0)
    R2 = float(np.einsum("ij,ij->", Hdiff, R0) / ss_total)

    rng = np.random.default_rng(seed)
    ge = 0
    for pi in _perm_indices(n, blocks, n_perm, rng):
        Rp = R0[np.ix_(pi, pi)]
        if F_of(Rp) >= F_obs - 1e-12:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    return DBResult(F=float(F_obs), p=float(p), R2=R2, df1=int(df1), df2=int(df2),
                    n_perm=n_perm, n_used_perms=_n_restricted_perms(blocks))


# ── public wrappers ──────────────────────────────────────────────────────────────────────────
def permanova(D: np.ndarray, groups: _ArrayLike, blocks: Optional[_ArrayLike] = None,
              n_perm: int = 999, seed: int = 0) -> DBResult:
    """One-factor PERMANOVA (McArdle–Anderson). `blocks` restricts permutation to within-family."""
    G = gower_G(D)
    n = G.shape[0]
    Xfull = _stack(n, [_design(groups)])
    X0 = np.ones((n, 1))
    b = None if blocks is None else np.asarray(blocks)
    return _dblm(G, Xfull, X0, b, n_perm, seed)


def adonis_term(D: np.ndarray, term: _ArrayLike,
                covars: Optional[Union[_ArrayLike, Sequence[_ArrayLike]]] = None,
                term_ordinal: bool = False, blocks: Optional[_ArrayLike] = None,
                n_perm: int = 999, seed: int = 0) -> DBResult:
    """Test `term` adjusted for `covars` (Freedman–Lane). term_ordinal=True -> 1-df monotonic test.

    covars may be one array or a list of arrays; each categorical unless float dtype. With
    covars=None this reduces to a marginal test (identical to permanova for a categorical term).
    """
    G = gower_G(D)
    n = G.shape[0]
    if covars is None:
        cov_blocks = []
    elif isinstance(covars, (list, tuple)) and len(covars) and np.ndim(covars[0]) >= 1:
        cov_blocks = [_design(c) for c in covars]
    else:
        cov_blocks = [_design(covars)]
    X0 = _stack(n, cov_blocks)
    Xfull = _stack(n, cov_blocks + [_design(term, ordinal=term_ordinal)])
    b = None if blocks is None else np.asarray(blocks)
    return _dblm(G, Xfull, X0, b, n_perm, seed)


def dbrda_trend(D: np.ndarray, score: _ArrayLike,
                covars: Optional[Union[_ArrayLike, Sequence[_ArrayLike]]] = None,
                blocks: Optional[_ArrayLike] = None, n_perm: int = 999, seed: int = 0) -> DBResult:
    """Ordinal/monotonic 1-df test: does environment march along `score` (fixity as 1..k)."""
    return adonis_term(D, score, covars=covars, term_ordinal=True,
                       blocks=blocks, n_perm=n_perm, seed=seed)


# ── PERMDISP (betadisper, Anderson 2006) ─────────────────────────────────────────────────────
def _anova_F(z: np.ndarray, groups: np.ndarray):
    labs = list(dict.fromkeys(groups.tolist()))
    n, a = len(z), len(labs)
    grand = z.mean()
    ssb = sum(((groups == g).sum()) * (z[groups == g].mean() - grand) ** 2 for g in labs)
    ssw = sum(((z[groups == g] - z[groups == g].mean()) ** 2).sum() for g in labs)
    F = (ssb / (a - 1)) / (ssw / (n - a)) if ssw > 0 else np.inf
    return F, a


def permdisp(D: np.ndarray, groups: _ArrayLike, blocks: Optional[_ArrayLike] = None,
             n_perm: int = 999, seed: int = 0) -> DispResult:
    """Homogeneity of multivariate dispersions across `groups`. Handles non-Euclidean D via the
    Anderson real/imaginary split (subtract negative-eigenvalue contributions from the centroid
    distance). For Euclidean D (our Climate-envelope distance) G is PSD and the split is inert."""
    groups = np.asarray(groups)
    G = gower_G(D)
    n = G.shape[0]
    lam, U = np.linalg.eigh(G)
    keep = np.abs(lam) > 1e-8
    lam, U = lam[keep], U[:, keep]
    coords = U * np.sqrt(np.abs(lam))
    sgn = np.sign(lam)

    def dispersions(gr: np.ndarray) -> np.ndarray:
        z = np.empty(n)
        for g in dict.fromkeys(gr.tolist()):
            m = gr == g
            c = coords[m].mean(axis=0)
            diff2 = (coords[m] - c) ** 2
            real = diff2[:, sgn > 0].sum(axis=1)
            imag = diff2[:, sgn < 0].sum(axis=1)
            z[m] = np.sqrt(np.clip(real - imag, 0, None))
        return z

    F_obs, a = _anova_F(dispersions(groups), groups)
    df1, df2 = a - 1, n - a
    rng = np.random.default_rng(seed)
    ge = 0
    for pi in _perm_indices(n, None if blocks is None else np.asarray(blocks), n_perm, rng):
        gr = groups[pi]
        F_p, _ = _anova_F(dispersions(gr), gr)
        if F_p >= F_obs - 1e-12:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    gm = {g: float(dispersions(groups)[groups == g].mean()) for g in dict.fromkeys(groups.tolist())}
    return DispResult(F=float(F_obs), p=float(p), group_mean_dist=gm,
                      df1=int(df1), df2=int(df2), n_perm=n_perm)
