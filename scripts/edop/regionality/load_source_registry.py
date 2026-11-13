"""Load documentation/EDOPS_source_registry.yaml into public.source_registry (regionality WO-04, Part A).

One row per source: id, status, table_names as plain columns; `selects` and `describes` as jsonb. Creates the table if
missing, then replaces all rows in one transaction, so a re-run gives the same table. Touches only this table.

    python scripts/edop/regionality/load_source_registry.py
"""
import sys
from pathlib import Path

import yaml
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from app.db.connection import db_connect  # noqa: E402

YAML_PATH = ROOT / 'documentation' / 'EDOPS_source_registry.yaml'

DDL = """
CREATE TABLE IF NOT EXISTS public.source_registry (
    id          text        PRIMARY KEY,
    status      text        NOT NULL,
    table_names text[]      NOT NULL DEFAULT '{}',
    selects     jsonb       NOT NULL,
    describes   jsonb       NOT NULL,
    loaded_at   timestamptz NOT NULL DEFAULT now()
)
"""


def table_names(selects):
    t = selects.get('table')
    return [] if t is None else [t] if isinstance(t, str) else list(t)


def main():
    sources = yaml.safe_load(YAML_PATH.read_text(encoding='utf-8'))['sources']
    with db_connect() as conn:
        with conn.transaction():
            conn.execute(DDL)
            conn.execute('DELETE FROM public.source_registry')
            for s in sources:
                conn.execute(
                    'INSERT INTO public.source_registry (id, status, table_names, selects, describes) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (s['id'], s['selects']['status'], table_names(s['selects']), Jsonb(s['selects']), Jsonb(s['describes'])))
        rows = conn.execute('SELECT id, status, table_names FROM public.source_registry ORDER BY id').fetchall()
    for r in rows:
        print(r)
    print(f'{len(rows)} rows in public.source_registry')


if __name__ == '__main__':
    main()
