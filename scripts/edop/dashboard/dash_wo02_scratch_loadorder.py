"""SCRATCH (dash WO-02): drive /sandbox through its own controls and time when each control and tab becomes ready."""
import json
import time
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8000'
JS_SIG_DONE = "(() => { const p = document.getElementById('v3-sig-content'); return !!p && p.innerText.trim() !== '' && !p.innerText.includes('Loading signature'); })()"


def enabled(id_):
    return f"(() => {{ const e = document.getElementById('{id_}'); return !!e && !e.disabled && !e.classList.contains('disabled'); }})()"


def timed_wait(pg, js, t0, timeout=90000):
    try:
        pg.wait_for_function(js, timeout=timeout)
        return round(time.time() - t0, 2)
    except Exception as e:
        return f'timeout ({type(e).__name__})'


def settlement(pg, value):
    out = {}
    t0 = time.time()
    pg.select_option('#v3-example-select', value=value)
    out['sig_button_enabled_s'] = timed_wait(pg, enabled('v3-sig-btn'), t0, 10000)
    t1 = time.time()
    pg.click('#v3-sig-btn')
    out['signature_tab_filled_s'] = timed_wait(pg, JS_SIG_DONE, t1)
    for name, id_ in [('analysis', 'v3-tab-analysis-btn'), ('seasonality', 'v3-tab-seasonality-btn'),
                      ('context', 'v3-tab-context-btn'), ('similarity', 'v3-tab-similarity-btn')]:
        out[f'{name}_tab_enabled_s'] = timed_wait(pg, enabled(id_), t1)
    return out


def polity(pg, value):
    out = {}
    pg.click('#v3-tab-polities-btn')
    t0 = time.time()
    pg.select_option('#v3-polity-example', value=value)
    out['polity_sig_button_enabled_s'] = timed_wait(pg, enabled('v3-polity-sig-btn'), t0)
    out['slices'] = pg.evaluate("document.getElementById('v3-slice-select').options.length")
    out['resolver_year'] = pg.evaluate("document.getElementById('v3-resolver-year').value")
    t1 = time.time()
    pg.click('#v3-polity-sig-btn')
    out['signature_tab_filled_s'] = timed_wait(pg, JS_SIG_DONE, t1)
    return out


with sync_playwright() as p:
    print('health:', urllib.request.urlopen(BASE + '/api/health', timeout=10).status)
    b = p.chromium.launch(headless=True)
    res = {}
    for label, fn, arg in [('settlement Tbilisi 1150-1250', settlement, '41.6938,44.8015|Tbilisi|1150|1250'),
                           ('polity Northern Song', polity, 'polity|Northern Song')]:
        pg = b.new_page(viewport={'width': 1400, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
        t = time.time()
        pg.goto(BASE + '/sandbox', wait_until='load')
        res[label] = {'page_load_s': round(time.time() - t, 2)}
        res[label].update(fn(pg, arg))
        res[label]['page_errors'] = errs[:3]
        pg.close()
    b.close()
print(json.dumps(res, indent=1))
