"""
WO5 Part B -- schema recon before designing the Context data path.

Checks: what basin08_scores already has precomputed (avoids re-deriving global
percentiles for variables that already have a materialized column), whether a
basin06_scores analog exists, and confirms the raw columns behind the WO's
candidate variable list actually exist on basin06/basin08.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

conn = db_connect()

queries = {
    "basin08_scores columns": """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'basin08_scores'
        ORDER BY ordinal_position
    """,
    "basin06_scores exists?": """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'basin06_scores'
    """,
    "candidate raw columns present on basin06": """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'basin06'
          AND column_name IN ('ele_mt_sav', 'ari_ix_sav', 'run_mm_syr',
                               'slp_dg_sav', 'pre_mm_syr', 'tmp_dc_syr')
        ORDER BY column_name
    """,
}

for label, sql in queries.items():
    print(f"\n=== {label} ===")
    print(sql.strip())
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    for r in rows:
        print(" ", r[0])
    print(f"  ({len(rows)} rows)")

conn.close()
