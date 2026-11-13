"""Source registry (regionality WO-04, Part A): the YAML covers what the signature reads."""
import csv
from pathlib import Path

import pytest
import yaml

from app.db.connection import db_connect

ROOT = Path(__file__).resolve().parents[2]
YAML_PATH = ROOT / 'documentation' / 'EDOPS_source_registry.yaml'
CATALOG_PATH = ROOT / 'documentation' / 'EDOPS_variable_catalog_v0.4.tsv'

# Every source the signature reads or credits (CLAUDE.md database section, engine and public routes).
EXPECTED_IDS = {'lmr_v2_1', 'hyde_3_5', 'evolv2k_v4', 'geda', 'cliopatria', 'basinatlas_v1', 'edops_derived',
                'opentopodata_mapzen', 'open_meteo_elevation'}
# Catalog keys that more than one entry claims: the derived variable and the two services that can supply it.
SHARED_KEYS = {'elevation_point'}


@pytest.fixture(scope='module')
def sources():
    return yaml.safe_load(YAML_PATH.read_text(encoding='utf-8'))['sources']


@pytest.fixture(scope='module')
def catalog():
    with open(CATALOG_PATH, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def _as_list(x):
    return [] if x is None else [x] if isinstance(x, str) else list(x)


def _table_names(s):
    return _as_list(s['selects'].get('table'))


def _claims(sources):
    """(catalog `source` values claimed whole, {catalog key: [source ids]}) from the `variables` of each entry."""
    by_source, by_key = {}, {}
    for s in sources:
        v = s['selects'].get('variables')
        if isinstance(v, dict):
            for c in _as_list(v['catalog_source']):
                by_source.setdefault(c, []).append(s['id'])
        else:
            for e in v or []:
                for k in _as_list(e.get('catalog')):
                    by_key.setdefault(k, []).append(s['id'])
    return by_source, by_key


def test_every_source_has_an_entry_with_both_blocks(sources):
    assert {s['id'] for s in sources} == EXPECTED_IDS
    for s in sources:
        assert s['selects'].get('status') in ('served', 'stored'), s['id']
        assert s.get('describes', {}).get('name'), s['id']


def test_every_named_table_exists(sources):
    with db_connect() as conn:
        for s in sources:
            for t in _table_names(s):
                assert conn.execute('SELECT to_regclass(%s)', (t,)).fetchone()[0] is not None, f'{s["id"]}: {t} missing'


def test_every_catalog_variable_is_claimed(sources, catalog):
    by_source, by_key = _claims(sources)
    unclaimed = [r['schema_key'] for r in catalog if not by_source.get(r['source']) and not by_key.get(r['schema_key'])]
    assert unclaimed == []
    assert [k for k in by_key if k not in {r['schema_key'] for r in catalog}] == []


def test_a_catalog_variable_has_one_owner_except_the_shared_ones(sources, catalog):
    by_source, by_key = _claims(sources)
    multi = {r['schema_key'] for r in catalog if len(by_source.get(r['source'], []) + by_key.get(r['schema_key'], [])) > 1}
    assert multi == SHARED_KEYS
