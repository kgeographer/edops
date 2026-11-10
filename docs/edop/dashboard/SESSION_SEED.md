# Session seed — Dashboard phase (2026-10-25)

EDOPS is changing phase. v0.4.1 is stable, in production, and frozen. `main` equals prod, and any v0.4
bugfix or tweak is made on `main`. Read `CLAUDE.md` first, then the latest `logs/session_log_*.md`
(`20261025` covers this transition).

Two large phases follow, in this order:

1. **Dashboard (active).** A general-purpose front door for `edops.computingplace.org`, more broadly useful
   than the Sandbox / Workbench / Explorer trio. Explorer stays as is. Work happens on branch `dashboard`,
   which has a stub page at `/dashboard`. It will borrow heavily from `sandbox.html` and somewhat from
   `workbench.html`. Copy first, leave the originals untouched, and extract shared code only once the design
   settles. The backend and the public API (`/health`, `/signature`) are expected to survive. Nothing from this
   branch deploys for a good while, so preview it locally.
2. **Regional (non-global) temporal data (next).** Adding datasets that don't cover the globe has real
   consequences for the data model, the API's handling of missing coverage, and the dashboard's UX. Seed
   material is on the remote branch `claude/remote-phone-file-access-hvttai`: a regional-layers framing doc and
   a drought-atlas memo. Don't merge it. Read it when this phase starts.

This is a three-way effort. Karl does preliminary design with Opus, producing work-order specs. Karl brings
those to CC, which experiments and implements. Don't start coding, and don't change files, until Karl agrees to
a stated list. After a proposal, say how you understood it first.

Work starts in experimental notebooks under `notebooks/edop/dashboard/`, as in earlier phases. Karl runs the
cells himself, so never run notebook cells from Bash. Findings go in `docs/edop/dashboard/wo{nn}_findings.md`,
with a tracker created when the first work order arrives. Keep the logs, commits and tracker notes concise.
Nothing is committed without Karl's review, and every UI change is reviewed in his browser first.
