# CC work order — WO10b: coherence flag on distribution_only

**Date:** 2026-06-24 · branch off WO10 · one small change, stop for review.

---

Settles the one open contract item (§7). `distribution_only` rows (`temp_min`, `temp_max`) currently ship `representative_score` with `coherence=null` — the one place a headline goes out without its trust flag.

**Change:** in `aggregate_b5`, emit `coherence` on the distribution_only path using the same spread test B1 uses — `concentrated` if weighted (p90 − p10) < T (T=20), else `spread`. B5 already computes the spread; this just surfaces the verdict instead of withholding it. The `extreme` path (`river_area`) is unchanged — `coherence=null` stays (no concentrated/spread concept for an extremum).

**Re-freeze:** this diverges from the frozen NaN deliberately (same blessed-deviation pattern as the modal label / LMR caveat). Re-freeze the `coherence` column on the 2 distribution_only rows of `step3_results.tsv` — prove the only delta is `coherence` on those 2 rows, nothing else. **Karl signs off the re-freeze before commit.**

**Amendments file:** move the "distribution_only coherence" item from **Pending** to **Folded** in `contract_amendments.md`, dated 2026-06-24. Pending is then empty.

On completion: report the re-freeze diff (2 rows, `coherence` only), confirm Pending is clear, update the tracker. Stop. Final engine assembly is next.
