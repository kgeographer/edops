"""WO-05 item 3: what the browser does with a long Band T span (Lviv, single basin, Dashboard on the local server).

For each span: seconds from page load until the Band T block is drawn, DOM node count of the Signature pane, the
HYDE table's columns and width, and the JS heap if the browser reports it. Usage: python dash_wo05_span_render.py [base_url]
"""
import sys
import time

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
SPANS = [(1300, 1399), (1000, 1399), (1000, 1999), (1900, 2000)]    # 100, 400, 1000 years, and 100 years with annual HYDE steps
URL = BASE + "/dashboard?lat=49.8397&lon=24.0297&name=Lviv&bands=T&from_year={f}&to_year={t}&view=signature&v=1"

with sync_playwright() as p:
    browser = p.chromium.launch()
    for f, t in SPANS:
        page = browser.new_page()
        t0 = time.perf_counter()
        page.goto(URL.format(f=f, t=t), wait_until="load")
        page.wait_for_selector("#v3-t-geda", timeout=300000)
        dt = time.perf_counter() - t0
        info = page.evaluate("""() => {
          const pane = document.getElementById('v3-sig-content');
          const tbl = [...pane.querySelectorAll('table')].find(x => x.innerText.includes('Cropland'));
          return { nodes: pane.getElementsByTagName('*').length,
                   hydeCols: tbl ? tbl.rows[0].cells.length - 1 : 0,
                   hydeWidthPx: tbl ? Math.round(tbl.scrollWidth) : 0,
                   paneWidthPx: Math.round(pane.clientWidth),
                   heapMB: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : null };
        }""")
        print(f"{f}-{t} ({t - f + 1} years): {dt:.1f} s to draw; {info}", flush=True)
        page.close()
    browser.close()
