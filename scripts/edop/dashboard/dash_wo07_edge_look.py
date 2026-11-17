"""WO-07 item 3: spans just inside and just over the span gate's limits, and spans that cross 1950.

Local server only (default http://localhost:8000). For each case it opens the Dashboard on the Signature tab by link,
times the load until Band T is drawn, records the HYDE table's columns and width against the pane, the DOM size and any
page errors, and screenshots the Band T accordion. Writes output/edop/dashboard/wo07_edge/wo07_edge_look.csv and the
screenshots beside it. Usage: python dash_wo07_edge_look.py [base_url]
"""
import csv
import sys
import time
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
OUT = Path(__file__).resolve().parents[3] / "output" / "edop" / "dashboard" / "wo07_edge"

LVIV = dict(lat=49.8397, lon=24.0297, name="Lviv")
SANTA_FE = dict(lat=35.687, lon=-105.9378, name="Santa Fe")
# single basin and ring: limit 12 steps; polity: 9 (the gate as proposed). 0-1100 is 12 steps, 0-1200 is 13; 1000-1710 is 9, 1000-1720 is 10.
CASES = (
    [("Lviv single", "single_basin", LVIV, s) for s in [(0, 1100), (0, 1200), (1940, 1960), (1900, 2000)]]
    + [("Santa Fe single", "single_basin", SANTA_FE, s) for s in [(0, 1100), (0, 1200), (1900, 2000)]]
    + [("Lviv ring", "basin_ring", LVIV, s) for s in [(0, 1100), (0, 1200), (1900, 2000)]]
    + [("Kingdom of Croatia", "polity", "Kingdom of Croatia", s) for s in [(1000, 1710), (1000, 1720), (1900, 2000)]]
    + [("Northern Song", "polity", "Northern Song", s) for s in [(1000, 1710), (1000, 1720), (1000, 1799), (1900, 2000)]]
)


def url(scope, place, span):
    f, t = span
    if scope == "polity":
        return f"{BASE}/dashboard?scope=polity&polity={quote(place)}&year=1000&bands=ABCDET&from_year={f}&to_year={t}&view=signature&v=1"
    return (f"{BASE}/dashboard?scope={scope}&lat={place['lat']}&lon={place['lon']}&name={quote(place['name'])}"
            f"&bands=ABCDET&from_year={f}&to_year={t}&view=signature&v=1")


DONE = "document.getElementById('v3-acc-T') !== null && document.getElementById('v3-tab-sig-spin').classList.contains('d-none')"
INFO = """() => {
  const pane = document.getElementById('v3-sig-content');
  const tbl = [...pane.querySelectorAll('table')].find(x => x.innerText.includes('Cropland'));
  return { nodes: pane.getElementsByTagName('*').length, hydeCols: tbl ? tbl.rows[0].cells.length - 1 : 0,
           hydeWidthPx: tbl ? Math.round(tbl.scrollWidth) : 0, paneWidthPx: Math.round(pane.clientWidth),
           warned: !document.getElementById('v3-t-span-warn').classList.contains('d-none') };
}"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, scope, place, span in CASES:
            page = browser.new_page(viewport={"width": 1400, "height": 1000})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            t0 = time.perf_counter()
            page.goto(url(scope, place, span), wait_until="load")
            try:
                page.wait_for_function(DONE, timeout=300000)
                secs = round(time.perf_counter() - t0, 1)
                info = page.evaluate(INFO)
                steps = page.evaluate(f"EdopsSpanGate.stepsIn({span[0]}, {span[1]})")
                shot = OUT / f"{label.replace(' ', '_')}_{span[0]}-{span[1]}.png"
                page.locator("#v3-acc-T").screenshot(path=str(shot))
            except Exception as e:                      # a case that fails is recorded, not fatal
                secs, info, steps, shot = round(time.perf_counter() - t0, 1), {}, None, ""
                errors.append(f"{type(e).__name__}: {str(e)[:120]}")
            row = dict(case=label, start=span[0], end=span[1], steps=steps, seconds_to_band_t=secs, **info,
                       errors="; ".join(errors), screenshot=shot.name if shot else "")
            rows.append(row)
            print(row, flush=True)
            page.close()
        browser.close()
    keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
    with open(OUT / "wo07_edge_look.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("wrote", OUT / "wo07_edge_look.csv")


if __name__ == "__main__":
    main()
