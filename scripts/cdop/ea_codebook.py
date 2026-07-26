"""EA codebook reference dump — for choosing the next trait to probe (WO8a follow-up).

Reads the D-PLACE CLDF StructureDataset (data/dplace/cldf/{variables,codes,data}.csv) and, if
present, the WO8a substrate (output/cdop/wo8a_substrate.parquet) to report coverage among the
basin-joined societies. Writes a human-scannable markdown reference:

    output/cdop/ea_codebook_reference.md

Two sections: (1) an index table — one line per EA variable (ID · type · coverage · name),
sorted by category; (2) detail — each variable's code labels. Re-run any time:

    python scripts/cdop/ea_codebook.py

Not tied to the app or DB (pure local-CSV read). The DB mirrors it as dplace.variables /
dplace.codes if you prefer DBeaver.
"""
from __future__ import annotations

import csv
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLDF = ROOT / "data" / "dplace" / "cldf"
OUT = ROOT / "output" / "cdop"
OUT.mkdir(parents=True, exist_ok=True)
OUT_MD = OUT / "ea_codebook_reference.md"

EA = "dplace-dataset-ea"


def _col(fieldnames, *candidates):
    """First fieldname matching any candidate (case-insensitive)."""
    low = {c.lower(): c for c in fieldnames}
    for cand in candidates:
        if cand in low:
            return low[cand]
    raise KeyError(f"none of {candidates} in {fieldnames}")


def load_joined_soc_ids():
    """Set of society ids in the WO8a substrate, or None if the parquet isn't present."""
    pq = OUT / "wo8a_substrate.parquet"
    if not pq.exists():
        return None
    import pandas as pd
    return set(pd.read_parquet(pq)["soc_id"].astype(str))


def main():
    # Variables (EA slice)
    with open(CLDF / "variables.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    ea_vars = [r for r in rows if r["Contribution_ID"] == EA]

    # Codes -> {var_id: [(code_id, label), ...]}, and the set of "missing"-type code ids
    codes_by_var: dict[str, list] = collections.defaultdict(list)
    missing_code_ids: set[str] = set()
    with open(CLDF / "codes.csv", newline="") as f:
        cr = csv.DictReader(f)
        c_id, c_var, c_name = (_col(cr.fieldnames, "id"),
                               _col(cr.fieldnames, "var_id", "variable_id", "parameter_id"),
                               _col(cr.fieldnames, "name"))
        for r in cr:
            codes_by_var[r[c_var]].append((r[c_id], r[c_name]))
            nm = (r[c_name] or "").lower()
            if "missing" in nm or nm in ("two or more sources",):
                missing_code_ids.add(r[c_id])

    # Coverage among joined societies (non-missing codes only)
    joined = load_joined_soc_ids()
    cov: dict[str, set] = collections.defaultdict(set)
    with open(CLDF / "data.csv", newline="") as f:
        dr = csv.DictReader(f)
        d_soc, d_var = (_col(dr.fieldnames, "soc_id", "society_id"),
                        _col(dr.fieldnames, "var_id", "variable_id", "parameter_id"))
        d_code = _col(dr.fieldnames, "code_id", "code", "value")
        for r in dr:
            if joined is not None and r[d_soc] not in joined:
                continue
            if r[d_code] in missing_code_ids:
                continue
            cov[r[d_var]].add(r[d_soc])

    denom = len(joined) if joined is not None else None
    by_cat = collections.defaultdict(list)
    for v in ea_vars:
        by_cat[v["category"] or "(uncategorised)"].append(v)

    lines = ["# EA codebook reference (94 variables)", ""]
    lines.append(f"Source: `data/dplace/cldf/`. Coverage = distinct non-missing-coded societies "
                 + (f"among the {denom} WO8a basin-joined set." if denom else "(substrate parquet not found; coverage omitted)."))
    lines.append("Regenerate: `python scripts/cdop/ea_codebook.py`. DB mirror: `dplace.variables` / `dplace.codes`.")
    lines.append("")

    # Section 1 — index
    lines.append("## Index (by category)")
    lines.append("")
    lines.append("| ID | type | coverage | variable |")
    lines.append("|---|---|---|---|")
    for cat in sorted(by_cat):
        lines.append(f"| | | | **{cat}** |")
        for v in sorted(by_cat[cat], key=lambda x: x["ID"]):
            n = len(cov.get(v["ID"], ()))
            covs = f"{n}/{denom}" if denom else str(n)
            lines.append(f"| {v['ID']} | {v['type']} | {covs} | {v['Name']} |")
    lines.append("")

    # Section 2 — detail with code labels
    lines.append("## Detail — code categories")
    lines.append("")
    for cat in sorted(by_cat):
        lines.append(f"### {cat}")
        lines.append("")
        for v in sorted(by_cat[cat], key=lambda x: x["ID"]):
            n = len(cov.get(v["ID"], ()))
            covs = f"n={n}/{denom}" if denom else f"n={n}"
            lines.append(f"**{v['ID']} — {v['Name']}**  _[{v['type']} · {covs}]_")
            desc = (v.get("Description") or "").strip()
            if desc:
                lines.append(f"> {desc}")
            cs = codes_by_var.get(v["ID"], [])
            if cs:
                for _cid, label in cs:
                    lines.append(f"  - {label}")
            else:
                lines.append("  - (no discrete codes — continuous/ordinal value)")
            lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD}  ({len(ea_vars)} EA variables, {len(by_cat)} categories, "
          f"coverage denom={denom})")


if __name__ == "__main__":
    main()
