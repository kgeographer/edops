"""Capture the regression baseline: reference payloads for tests/regionality/baseline.py REQUESTS.

Calls the real routes through FastAPI's test client against the local database (GET only); no server needed.
Refuses to overwrite a reference file without --force: re-capture only at a stage boundary, with Karl's approval.

    python scripts/edop/regionality/capture_baseline.py                  # captures any request without a reference file
    python scripts/edop/regionality/capture_baseline.py --force          # re-captures all
    python scripts/edop/regionality/capture_baseline.py kyiv_bandT_1300_1400 --force
"""
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from tests.regionality import baseline as bl  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('names', nargs='*', help='requests to capture (default: all)')
ap.add_argument('--force', action='store_true', help='overwrite existing reference files')
a = ap.parse_args()

names = a.names or list(bl.REQUESTS)
client = TestClient(app)
for n in names:
    if bl.ref_path(n).exists() and not a.force:
        print(f'{n}: reference exists, skipped (use --force)')
        continue
    payload = bl.fetch(client, n)
    bl.save_ref(n, payload)
    print(f'{n}: {bl.ref_path(n).stat().st_size / 1e3:.0f} kB')

head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
manifest = {'captured': str(datetime.date.today()), 'git_head': head,
            'requests': {n: {'route': r, 'params': p} for n, (r, p) in bl.REQUESTS.items()}}
(bl.REF_DIR / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1) + '\n')
