# What has changed since EDOPS 0.4

- Sandbox and Workbench page replaced by Dashboard and Using EDOPS respectively
- Example signatures for settlements and polities enabled on EDOPS splash page, edops.computingplace.org
- Choice of example from a dropdown on either splash or Dashboard loads a signature immediately
- Rule-based generation of Profiles (so far, only for settlement examples, Level 06 basins), loading in a new Profile tab on Dashboard. WIP.
- New backend "harness" enabling addition of regional datasets; first is Great Eurasian Drought Atlas (GEDA; summer scPDSI z-scores, 1000-2020)
- New Using EDOPS page to include worked examples of applications of EDOPS signatures; Societies and African Regions content from the former Workbench page ported so far, WIP.
- Atlas page for viewing global precipitation modality patterns moved to Data Explorer page
- Permalink button, with links that open Dashboard at a place and a tab
- Time series tab in the Dashboard (stub; long Band T spans will point there)
- Band T states which sources answered and why any did not; every API response carries a `sources` block, and a source registry (one YAML file) holds citations and licences
- HYDE land use drawn as a line chart instead of a table
- HYDE queries 7 to 10 times faster; stepping through a polity's slices repaints the map in about 30 ms (was 2 to 15 s)
- limits on slow queries: a polity slice estimated over 5 s disables Get signature and says why, a buffer warns above 9 HYDE steps, and the server stops Band T's HYDE query at 20 s with a plain message
