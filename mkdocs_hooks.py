"""MkDocs build hook: docked-sidebar breakpoint override.

Material's tablet/desktop sidebar breakpoint (76.25em / 1220px, where the left nav switches
from a docked column to a hamburger drawer) is baked into its compiled CSS bundle with no
supported config knob -- confirmed via squidfunk/mkdocs-material#7130, where the maintainer
states the real fix requires a full SCSS recompile this project has no build tooling for, and
warns that a hand-written CSS override is fragile.

That fragility was confirmed directly (2026-08-07): a hand-written override in
docsite/stylesheets/extra.css tried to replicate Material's desktop-mode rules at a new
breakpoint, but only touched some of the ~18 interacting rules (sidebar position, nav
accordion, drawer overlay, search box width, content margins, ...) and broke nested-section
navigation outright.

This hook instead does a direct regex substitution on the *compiled* CSS after build, moving
every occurrence of the breakpoint pair in lockstep -- same literal Material-authored rules,
just relabeled to fire at a narrower width. Target is 48em (768px), matching Bootstrap's `md`
breakpoint (already the responsive line used elsewhere in this app's own UI) and confirmed
empirically against mkdocs.org's own getting-started page, which switches at ~765px.

Round 2 (same day): the first version only moved the primary-sidebar breakpoint pair
(76.25em/76.234375em) and missed that Material also pairs that same max-width with a SEPARATE
min-width:60em in 3 compound rules (verified against the untouched package source -- exactly
3, no more) -- one drives "TOC integrates into the primary nav" (.md-nav--integrated), the
other two are search-box width tweaks. The general replace corrupted all 3 into
`(min-width:60em) and (max-width:47.984375em)` -- a mathematically impossible range
(60em > 47.984375em) that can never fire. Fixed generally: any compound occurrence of the old
pair moves to (min-width:48em) and (max-width:59.984375em), matching the new primary-dock
point paired with Material's own unmoved secondary-sidebar threshold (60em) -- not hardcoded
per-selector, so it can't miss a 4th occurrence if one shows up in a future Material version.

Separately, `.md-nav--primary .md-nav__link[for=__toc]` (a *plain* max-width:59.984375em rule,
not part of the compound pattern above) was untouched and still-live in the new 48-60em
(768-960px) gap where the primary sidebar is now docked (not a mobile drawer) -- injecting a
mobile-only "jump to TOC" row into an otherwise-desktop sidebar, the vertical-gap-plus-stray-
icon Karl actually saw. Fixed narrowly, anchored on that specific selector, since
59.984375em/60em bare (non-compound) is shared with ~10 unrelated search-box rules that must
NOT move.
"""

import glob
import os
import re

_OLD_MIN = "76.25em"
_OLD_MAX = "76.234375em"
_NEW_MIN = "48em"
_NEW_MAX = "47.984375em"  # mirrors Material's own epsilon-below-the-round-number convention

# Any compound (min-width:60em) and (max-width:76.234375em) -- regardless of which selector
# follows -- moves as a unit. Must run BEFORE the general bare replacement below (whose target
# string is a substring of this compound one, and would otherwise corrupt it the same way
# round 1 did).
_COMPOUND_RE = re.compile(r"\(min-width:60em\) and \(max-width:76\.234375em\)")
_COMPOUND_SUB = "(min-width:48em) and (max-width:59.984375em)"

# Narrowly targeted: only the primary-nav TOC-integration row, not the ~10 other rules sharing
# this same bare breakpoint (search box sizing, scroll-lock, etc.).
_TOC_ROW_OLD = "@media screen and (max-width:59.984375em){.md-nav--primary .md-nav__link[for=__toc]"
_TOC_ROW_NEW = f"@media screen and (max-width:{_NEW_MAX}){{.md-nav--primary .md-nav__link[for=__toc]"


def on_post_build(config, **kwargs):
    pattern = os.path.join(config["site_dir"], "assets", "stylesheets", "main.*.min.css")
    matches = glob.glob(pattern)
    if not matches:
        print("WARNING: mkdocs_hooks — no compiled main.*.min.css found; sidebar breakpoint override skipped")
        return

    for path in matches:
        with open(path, "r", encoding="utf-8") as f:
            css = f.read()

        n_compound, css = _count_and_sub(_COMPOUND_RE, _COMPOUND_SUB, css)

        n_toc_row = css.count(_TOC_ROW_OLD)
        css = css.replace(_TOC_ROW_OLD, _TOC_ROW_NEW)

        n_min = css.count(f"min-width:{_OLD_MIN}")
        n_max = css.count(f"max-width:{_OLD_MAX}")
        css = css.replace(f"min-width:{_OLD_MIN}", f"min-width:{_NEW_MIN}")
        css = css.replace(f"max-width:{_OLD_MAX}", f"max-width:{_NEW_MAX}")

        with open(path, "w", encoding="utf-8") as f:
            f.write(css)

        print(f"mkdocs_hooks: sidebar breakpoint override — {n_min} min-width + {n_max} max-width "
              f"+ {n_compound} compound + {n_toc_row} toc-row occurrences moved in {os.path.basename(path)}")


def _count_and_sub(pattern, repl, text):
    n = len(pattern.findall(text))
    return n, pattern.sub(repl, text)
