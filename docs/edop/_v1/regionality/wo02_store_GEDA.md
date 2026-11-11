# WO-02 (regionality): store GEDA; explore on-the-fly basin delivery

Draft of 2026-11-11.

## Goal

Store GEDA as a raw grid table, the way LMR and HYDE are stored, and find out in a notebook what a basin query returns when GEDA is aggregated on the fly through the same Band T path as LMR. No API or app changes yet; the results decide what is delivered and how it is labelled.

## Decided (from WO-01)

- GEDA is the regional dataset; OWDA is out (legacy, superseded by its authors).
- LMR stays as is, globally from 0 CE. GEDA adds summer scPDSI from 1000 CE inside its footprint. Where both exist, both are served, labelled as separate products.
- Delivery at L6 only.
- Delivery follows the engine's principle for polygons: show the distribution of values within the basin, not only a single summary number.

## Part A: store

1. **Provenance.** `data/geda/geda_trim.nc` was downloaded from Zenodo (10.5281/zenodo.11059894), the authors' own deposit (Edward and Benjamin Cook), CC BY 4.0. The paper's Dropbox link points to a file of the same name; it is not used. Confirm the download is intact: compute the file's md5 fingerprint (`md5` on macOS) and check it equals the one Zenodo publishes for the file, `b05338614a43627b43acb878d860fb6a`. No other file is involved. Citation: Cook et al. 2024 and the Zenodo DOI. (This corrects WO-01, which said the file came from Dropbox.)
2. **Load** the grid into a table structured as the LMR grid table is, so the existing Band T machinery can read it with as little new code as possible. CC decides the schema from the LMR and HYDE precedents and reports it.
   - Mask the undeclared fill value (`> 1e30`) and NaN; store only the 28,970 cells with values.
   - Keep values as distributed: z-scores per cell against 1000–2020.
   - Record years as CE.
3. **Metadata** stored with the dataset (wherever LMR's lives): product name and version, citation, licence, variable (JJA scPDSI), units (standard deviations from the cell's 1000–2020 mean), grid (0.5°), years 1000–2020, and that 1990–2020 are observed (CRU TS 4.06), not reconstructed.
4. **Check** after loading: cell count, year range, value range, and spot values for the Kyiv and Tbilisi cells against the file.

## Part B: what is delivered now (inventory)

5. For LMR and HYDE, describe what the signature's Band T panel computes for a basin and year range: the per-year bars (which cells, which weights) and the line (what statistic). Use the LMR panel for a 3-cell basin, 500–600 CE, as the worked case. This is what GEDA would inherit. (The map is already known: it paints LMR temperature and precipitation directly from the grid and does not show PDSI.)
5a. **Cliopatria over Ukraine.** List the Cliopatria polities whose polygons overlap the Ukraine outline (`gaz.admin0`), with their year spans and the share of Ukraine each covers. Informational only: it shows whether the polity path could serve a Ukraine example without adding countries as a new kind of area.

## Part C: notebook experiments

Run GEDA through the Band T aggregation path, as for LMR, for these basins: the L6 basins containing Kyiv and Tbilisi; one large Ukraine basin (e.g. 2060448220, about 27 cells); one small one (e.g. 2060467040, no cell centre, `w_eff` 0.82); one basin at the edge of the footprint.

6. **The distribution per year:** for a sample year, the cell values and weights the panel would show.
7. **The summary line:** the per-year summary as LMR computes it, and how its spread over 1000–2020 compares with the cells' (expected to be narrower; by how much, per basin).
8. **An alternative line:** the basin's area-weighted series re-standardized against its own 1000–2020 record. Show both lines for the test basins, so Karl can see the difference.
9. **Small and edge basins:** what a basin with one or two cells, or partly outside the footprint, returns.
10. **Ranges:** what a year-range query returns (e.g. 1300–1400), following LMR's handling.
11. **Next to LMR:** for the Kyiv basin, the GEDA and LMR PDSI panels for the same range, as a user would see them.
12. **The 1990 check:** for the Ukraine basins, the difference in mean between 1960–1989 and 1990–2020, set against the differences between all other pairs of adjacent 30-year windows since 1000.

## Provisos

- Part A writes to the database; nothing else changes in the engine, API or app.
- Report numbers and pictures; no thresholds or verdicts. Karl decides what is delivered.
- Where the LMR path doesn't fit GEDA without changes, describe the change rather than making it.

## Deliverables

- The GEDA table and metadata (Part A), with the load script.
- Notebook: `notebooks/edop/regionality/wo02_geda_store_and_aggregate.ipynb`, following `notebooks/CLAUDE.md`.
- `wo02_results.md` and `wo02_summary.md`: one section per item, numbered as above; panel-style figures for items 6 to 11.

## Acceptance gate

GEDA is stored and checked, and every item in Parts B and C has an answer or a stated reason why not.
