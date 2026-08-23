# About the project

EDOPS is under continuing development toward a v1.0 release planned for February 2027. This page
covers where v0.4 (September 2026) stands, what's changed since v0.3, and what's still ahead. For
the full research framing — citations, worked examples, the complete argument — see the
[project summary](https://github.com/kgeographer/edops/blob/main/documentation/EDOP_summary_v04.md)
in the repository's `documentation/` folder. For the intellectual foundations behind Computing
Place, EDOP, and CDOP, see Karl Grossner's posts at [kgeographer.org](https://kgeographer.org/category/research/).

## Status

Three broad phases of work sit behind v0.4, each at a different point in its own arc:

- **Signature Design** — operational. The signature schema, its variable selection, and its
  temporal/spatial architecture are in active use, but remain open to revision as review and use
  surface new requirements.
- **Data Characterization (CHAR)** — closed. A systematic characterization of the signature
  datasets' distributional, spatial, and redundancy properties, undertaken before any correspondence
  testing. Its findings are a frozen deliverable.
- **Platform Implementation** — operational. The query engine, variable catalog growth, similarity
  tooling, and the Sandbox/Workbench/Data Explorer web interfaces built on top of both.

## Roadmap toward v1.0

Three phases of work lie ahead:

- **Signature extensions and refinement** — a set of variables (coastality's ecological and
  human-accessibility modes, terrain navigability) awaiting expert review before inclusion.
- **Further correspondence evaluation** — testing whether and where EDOPS signatures correspond to
  independently attested cultural and environmental phenomena. Substantial exploratory work has
  already started here using D-PLACE societies data. Future candidate resources include the [Seshat Global History Databank](https://www.seshat-db.com/) data linked to the [Cliopatria polities](https://github.com/Seshat-Global-History-Databank/cliopatria) already in place and the [Tracks of Yu Yellow River database](https://tracksofyu.github.io/).
- **Dashboard design and development** — a new user-facing tool, the project's intended primary
  public interface, informed by and likely borrowing from Sandbox and Workbench. Once it exists,
  those two pages are expected to recede into eyes-only preview surfaces for developers and project
  members.

## What changed, v0.3 → v0.4

- This documentation site was added. 
- The interactive API docs moved to <a href="/api/schema" target="_blank" rel="noopener">/api/schema</a>.
- The signature service now supports areal queries in addition to a single containing basin for a place — basin ring and buffer scope choices for settlements, or an arbitrary polygon (so far, only historical polities from the Cliopatria dataset) — 
  Areal results are returned as distributions across their member basins, not averaged down to single values.
- The former **Lookup** page was replaced by a two-part **Sandbox**: a Settlements interface and a
  Polities interface, both built on the areal query architecture above.
- A new **Workbench** page was added, with correspondence-testing experiments that compare selected D-PLACE
  societies and World Heritage cities against their environmental signatures.
- **Data Explorer** (formerly "Explorer") is unchanged — it remains the data Characterization phasee's visual exhibit of the
  project dataset resources.
- Sandbox gained a new **Similarity panel** — a threshold test across precipitation, temperature,
  and terrain lenses, with adjustable tolerances per variable. Results are a set of basins worldwide (possibly empty) that match a place's environment on a given lens.
- Workbench's WH Cities panel gained ranked retrieval: for its small named corpus of World Heritage
  cities, results are ranked by environmental similarity or by textual similarity between
  Wikipedia-article language, rather than tested against a threshold.
- See [Similarity in EDOPS](similarity.md) for how these mechanisms actually differ, and why.

## Published findings

The EDA and ESDA characterization findings, the augmented variable codebook, and other research
records referenced above live in [the repository's `documentation/` folder](https://github.com/kgeographer/edops/tree/main/documentation), alongside the project summary.

*[EDA]: Exploratory Data Analysis
*[ESDA]: Exploratory Spatial Data Analysis
