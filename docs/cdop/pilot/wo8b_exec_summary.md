# WO8b — executive summary (for Opus / next-WO scoping)

*(Numbers from the verified pipeline run — identical code and data to the notebook; family-restricted
permutation, drop-to-representative metric. Companion detail: `wo8b_findings.md` once finalized.)*

**One line:** Settlement fixity tracks environment — settled societies **concentrate in a narrow, favorable climatic band** (wet, warm, low-seasonality), gated chiefly by water, while mobile societies are the **wide fallback across the dry/cold/seasonal margins the band excludes** — a **target, not a floor**; and that is nearly the whole of it: net of the
farming decision, fixity's own environmental signal is negligible. The result worth carrying forward is
not about settlements at all — it is that the phylogenetic control demonstrably worked, deflating exactly
the axis predicted in advance.

## What WO8b was

The first **real test** in the correspondence arc (WO8a was the positive-control calibration). Trait:
**EA030 settlement fixity** (ordinal, nomadic → complex permanent), 918 basin-linked Ethnographic-Atlas
societies. Two tests together — **marginal** (does fixity track the Climate-envelope environment) and
**nested** (…net of subsistence — is it more than the farming-vs-foraging economy in disguise) — each
under the two controls WO8a deferred: **restricted permutation within language family** (the
phylogenetic / Galton null) and **PERMDISP** (so a spread difference isn't misread as a location shift).
A notebook, no engine/API/UI. Stats on a hand-rolled, unit-tested engine (`scripts/cdop/dbperm.py`).

## What we found

1. **Strong at face value — but ~84% is subsistence in disguise.** Fixity tracks climate strongly
   marginally (R²≈0.21), yet once economy is held constant its *own* signal collapses to R²≈0.01–0.03.
   Farming and settling are essentially one bundled act, not two things climate separately causes.

2. **The residual is negligible, not a second finding.** Net of economy, fixity's own environmental
   signal is R²≈0.01–0.03 — it clears the floor only because n≈900 makes trivial effects detectable. Read
   it as *no interpretable independent effect*: the story is that subsistence absorbed almost all of it,
   not that a small real signal remains. And because fixity and subsistence are near-collinear (the
   block-diagonal grid), even the 84% share is partly an artifact of their overlap, not a pure claim about
   nature.

3. **The distinction that matters — a target, not a floor.** Sedentary societies **cluster in a narrow
   favorable band** (wet/warm/low-seasonality, breadth 1.06); it is the **mobile** end that ranges widely
   (breadth 1.76), across the dry/cold/seasonal margins the band excludes. So climate does not merely
   *forbid* settling at the extremes — it **concentrates** settlement in the favorable band, chiefly via
   water (intensive agriculture reaches arid zones only by irrigation). This is the plain reading
   ("people settle where climate favors farming"), and the rigorous test earned it over a determinist
   over-claim — on observed per-group breadth (Cell 10), not intuition.

4. **Rainfall *timing* doesn't matter to fixity** — only *amount* and *warmth*, same as subsistence in
   WO8a. Adding the seasonality curve *dilutes* rather than sharpens the result; the hoped-for "settled
   life cares about *when* the rain comes" did not materialize.

5. **The phylogenetic control demonstrably bites — proof the instrument works.** The prediction was
   precise and confirmed: **temperature *level*** is phylogeny-inflated — its family-restricted p
   collapses to 0.020 (cousins share a latitude band) — while **aridity holds** (p=0.0005), the
   mechanistic agriculture-gate the prediction named. The robust picture is two-axis, not one: **thermal
   seasonality** also survives (p=0.0005) and is in fact the largest robust separator (R²=0.288; settled
   = equable climates, mobile = seasonal). The control's value is distinguishing the *inflated* axis
   (temperature level) from the *robust* ones (aridity, thermal seasonality) — not showing "temperature"
   is all ancestry.

## What it means

- **Reinforces WO8a one rung on.** "Environment sets bounds, doesn't determine" sharpens to: environment
  *permits* (gates the agriculture option via water) rather than *dictates*. Even a strong-hypothesis
  trait, net of the obvious confound and shared ancestry, has only a modest independent environmental
  signal.
- **The instrument earned trust for the contested tests — and this is the headline, not the fixity
  substance.** Watching temperature *level* deflate under the ancestry control while aridity holds is direct
  evidence the machinery separates real signal from phylogeny and confound — the credibility asset going
  into traits we don't already know the answer for. It is also the strongest short-form story for an
  external audience, because it is defensible on method grounds alone, no anthropology required: a named
  axis was predicted to evaporate under the control, and it did.
- **Sets expectations for 8c/8d** (political complexity → high gods): expect the same shape — face-value
  links that shrink under controls; the number that matters is the *residual after controls*, and an
  honest small effect beats a hunted-for "significant" one. With n≈900, even trivial effects clear
  significance, so the gate reads **effect size, not p-value**.

## Open questions / drill points for the WO author

1. **Reporting stance — decided: a negligible residual is not a positive.** Report the *confound share*
   as the headline; report residuals below a pre-set effect-size floor as *no interpretable independent
   effect*, never as "small real." Set the floor before 8c's number is seen, so it can't be motivated by
   the result — the guard against a three-rung probe accreting slivers into an overclaim.
2. **The breadth-vs-centre result (PERMDISP).** Fixity groups differ in environmental *range*, not just
   location — a genuine finding, but it means the marginal factor number mixes the two. Decide whether to
   lead with the ordinal-trend and nested reads (cleaner) and whether a 3-level `complex→sedentary` merge
   (group sizes 591 vs 24) is worth a robustness line.
3. **Container caveat.** Disclosed, not corrected; the conditional robustness rerun (drop >2 °C
   basin-site-gap societies) is unnecessary here — the result isn't borderline.
4. **8c trait framing.** Political complexity routes through subsistence/surplus too — the nested design
   is even more essential there; worth deciding the covariate set (subsistence alone, or + fixity) before
   drafting.
