"""reg WO-07 item 2: the registry entry, the catalog row, the caveat texts and the data-sources lines for LBDA."""
import csv
import json
from pathlib import Path

import pytest

from app.api.routes_common import _data_sources_block
from app.db.connection import db_connect
from scripts.edop.areas import source_registry as sr
from scripts.edop.areas.engine import CAVEAT_TEXTS

pytestmark = pytest.mark.lbda

ROOT = Path(__file__).resolve().parents[2]


def test_entry_is_served_from_the_loaded_table():
    e = sr.entry('lbda_v3')
    assert e['selects']['status'] == 'served' and e['selects']['table'] == 'temporal.lbda_climate'
    assert e['selects']['footprint']['first_year_column'] == 'first_year' and e['selects']['coverage_rule']['per_year'] is True


def test_years_covered_match_the_loaded_table():
    first, last = sr.years_covered('lbda_v3')
    with db_connect() as conn:
        n = conn.execute('select max(array_length(pmdi, 1)) from temporal.lbda_climate').fetchone()[0]
        cells = conn.execute('select count(*) from temporal.lbda_climate').fetchone()[0]
    assert (first, last) == (0, n - 1) and sr.entry('lbda_v3')['selects']['footprint']['cells'] == cells


@pytest.mark.parametrize('year, keys', [(0, []), (1899, []), (1900, ['lbda_instrumental']), (2025, ['lbda_instrumental'])])
def test_instrumental_years_carry_the_caveat(year, keys):
    assert sr.year_caveats('lbda_v3', year) == keys


def test_every_caveat_key_the_entry_names_has_a_text():
    for c in sr.entry('lbda_v3')['selects']['caveats']:
        assert CAVEAT_TEXTS[c['key']]


def test_catalog_row():
    with open(ROOT / 'documentation' / 'EDOPS_variable_catalog_v0.4.tsv', encoding='utf-8') as f:
        rows = {r['schema_key']: r for r in csv.DictReader(f, delimiter='\t')}
    r = rows['lbda_pmdi']
    assert (r['band'], r['source'], r['api_key_s'], r['status']) == ('T', 'LBDA', 'lbda_pmdi', 'implemented') and 'PMDI' in r['units']


@pytest.mark.parametrize('schema', ['edops_schema_basin.json', 'edops_schema_area.json'])
def test_data_sources_lines_agree_with_the_code(schema):
    doc = json.loads((ROOT / 'documentation' / schema).read_text(encoding='utf-8'))
    line = _data_sources_block(6)['temporal_drought_conus']
    assert 'LBDA' in line and doc['meta']['data_sources']['temporal_drought_conus'] == line
