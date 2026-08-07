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
"""

import glob
import os

_OLD_MIN = "76.25em"
_OLD_MAX = "76.234375em"
_NEW_MIN = "48em"
_NEW_MAX = "47.984375em"  # mirrors Material's own epsilon-below-the-round-number convention


def on_post_build(config, **kwargs):
    pattern = os.path.join(config["site_dir"], "assets", "stylesheets", "main.*.min.css")
    matches = glob.glob(pattern)
    if not matches:
        print("WARNING: mkdocs_hooks — no compiled main.*.min.css found; sidebar breakpoint override skipped")
        return

    for path in matches:
        with open(path, "r", encoding="utf-8") as f:
            css = f.read()

        n_min = css.count(f"min-width:{_OLD_MIN}")
        n_max = css.count(f"max-width:{_OLD_MAX}")
        css = css.replace(f"min-width:{_OLD_MIN}", f"min-width:{_NEW_MIN}")
        css = css.replace(f"max-width:{_OLD_MAX}", f"max-width:{_NEW_MAX}")

        with open(path, "w", encoding="utf-8") as f:
            f.write(css)

        print(f"mkdocs_hooks: sidebar breakpoint override — {n_min} min-width + {n_max} max-width "
              f"occurrences moved to {_NEW_MIN}/{_NEW_MAX} in {os.path.basename(path)}")
