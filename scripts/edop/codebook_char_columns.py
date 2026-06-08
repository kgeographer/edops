"""
Add CHAR columns to edops_variable_catalog_v03, writing edops_variable_catalog_v03_char.tsv.

New columns added:
  I_L6, I_L8, scale_dir  — from spatial/first_cut_typology.csv
  distribution_notes      — templated from spatial/variable_characterization.csv (L6)
  concordance_notes       — generated from existing high_r_partner column

Column placement:
  concordance_notes  → after high_r_partner
  I_L6, I_L8, scale_dir → after typology_cluster / scale_sensitivity group
  distribution_notes → at end
"""

import pandas as pd

CB_IN  = "metadata/edops_variable_catalog_v03.tsv"
CB_OUT = "metadata/edops_variable_catalog_v03_char.tsv"
TYP    = "spatial/first_cut_typology.csv"
VC     = "spatial/variable_characterization.csv"

# ── Load ──────────────────────────────────────────────────────────────────────
cb  = pd.read_csv(CB_IN, sep="\t", dtype=str).fillna("")
typ = pd.read_csv(TYP)
vc  = pd.read_csv(VC)
vc_l6 = vc[vc["scale"] == "L6"].copy()

# ── 1. I_L6, I_L8, scale_dir ─────────────────────────────────────────────────
typ_sub = typ[["schema_key", "I_L6", "I_L8", "scale_dir"]].copy()
typ_sub["I_L6"]     = typ_sub["I_L6"].round(4).astype(str)
typ_sub["I_L8"]     = typ_sub["I_L8"].round(4).astype(str)
cb = cb.merge(typ_sub, on="schema_key", how="left")
cb["I_L6"]     = cb["I_L6"].fillna("deferred-phase4")
cb["I_L8"]     = cb["I_L8"].fillna("deferred-phase4")
cb["scale_dir"] = cb["scale_dir"].fillna("deferred-phase4")

# ── 2. distribution_notes ─────────────────────────────────────────────────────
def dist_note(row):
    parts = [f"Skewness {float(row['skewness']):.2f}"]
    zf = float(row["zero_fraction"])
    if zf > 0:
        parts.append(f"zero-fraction {zf:.2f}")
    mp = float(row["missing_pct"])
    if mp > 0:
        parts.append(f"missing {mp * 100:.1f}%")
    if str(row["log_transformed"]).lower() in ("true", "1"):
        parts.append("log-transformed for canonical Moran's I")
    return "; ".join(parts) + "."

vc_l6["distribution_notes"] = vc_l6.apply(dist_note, axis=1)
vc_notes = vc_l6[["schema_key", "distribution_notes"]].drop_duplicates("schema_key")
cb = cb.merge(vc_notes, on="schema_key", how="left")
cb["distribution_notes"] = cb["distribution_notes"].fillna("deferred-phase4")

# ── 3. concordance_notes ──────────────────────────────────────────────────────
def concordance_note(row):
    partner = str(row.get("high_r_partner", "")).strip()
    if not partner:
        return "No global co-variation |r| ≥ 0.90 with other signature variables."
    partners = [p.strip() for p in partner.split(";") if p.strip()]
    return f"Co-varies globally (|r| ≥ 0.90) with: {'; '.join(partners)}."

cb["concordance_notes"] = cb.apply(concordance_note, axis=1)

# ── Re-order columns ──────────────────────────────────────────────────────────
base = [
    "schema_key", "dimension", "band", "basin08_col_s", "basin08_col_u",
    "friendly_name", "type", "units", "s_u", "status", "atlas_id", "notes",
    "api_key_s", "api_key_u",
]
char = [
    "position_method", "position_notes",
    "high_r_partner", "concordance_notes",
    "typology_cluster", "scale_sensitivity", "I_L6", "I_L8", "scale_dir",
    "historical_validity",
    "informative_or_degenerate", "distribution_notes",
]
cb = cb[base + char]

# ── Write ─────────────────────────────────────────────────────────────────────
cb.to_csv(CB_OUT, sep="\t", index=False)
print(f"Written {CB_OUT}  shape={cb.shape}")
print("Columns:", list(cb.columns))
