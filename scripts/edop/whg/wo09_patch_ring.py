"""WO-09 item 1: give the flagged rows of the ring table their value.

The ring payload leaves `representative_raw` empty where the engine flags a share `outside_active_domain` (a value of 1% or less),
and member_values counted those rows as 0. basin06 holds the value (0 or 1), so it is written into the flagged rows; `status` is
unchanged. The original is kept as wo06_ring_values.pre_wo09.csv and the patch always reads from it, so a re-run gives the same table.
Run from the repo root: python -m scripts.edop.whg.wo09_patch_ring
"""
import shutil

import pandas as pd

from scripts.edop.whg import wo06_rings
from scripts.shared.db_utils import db_connect

CSV = wo06_rings.RING_CSV
BACKUP = CSV.with_name('wo06_ring_values.pre_wo09.csv')
# ring variable -> basin06 column (variable catalog); dist_sink is a distance, not a share, and is left alone
COLUMNS = {'cropland_extent': 'crp_pc_sse', 'cropland_extent_upstream': 'crp_pc_use',
           'pasture_extent': 'pst_pc_sse', 'pasture_extent_upstream': 'pst_pc_use',
           'karst': 'kar_pc_sse', 'karst_upstream': 'kar_pc_use', 'permafrost_extent': 'prm_pc_sse',
           'wet_pct_grp1': 'wet_pc_sg1', 'wet_pct_grp1_upstream': 'wet_pc_ug1',
           'wet_pct_grp2': 'wet_pc_sg2', 'wet_pct_grp2_upstream': 'wet_pc_ug2'}


def patched(t, conn):
    """The table with the value written into every flagged row of a variable in COLUMNS."""
    t = t.copy()
    for var, col in COLUMNS.items():
        m = (t['status'] == 'outside_active_domain') & (t['variable'] == var)
        ids = sorted(int(i) for i in t.loc[m, 'member'].unique())
        d = dict(conn.execute(f'SELECT hybas_id, {col} FROM public.basin06 WHERE hybas_id = ANY(%s)', (ids,)).fetchall())
        t.loc[m, 'value'] = t.loc[m, 'member'].map(lambda i: None if d.get(int(i)) is None else float(d[int(i)]))
    return t


def main():
    if not BACKUP.exists():
        shutil.copy2(CSV, BACKUP)
    t = pd.read_csv(BACKUP)
    out = patched(t, db_connect())
    out.to_csv(CSV, index=False)
    f = (t['status'] == 'outside_active_domain') & t['variable'].isin(COLUMNS)
    print(f'{len(out)} rows | {int(f.sum())} flagged rows given a value | {int((out.loc[f, "value"] > 0).sum())} of them above zero')


if __name__ == '__main__':
    main()
