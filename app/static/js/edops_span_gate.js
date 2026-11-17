/* Span gate for Band T on the Dashboard: counts the HYDE steps inside a span and says whether a scope's limit is exceeded.
   HYDE's steps (temporal.hyde_times, 128) are millennial to -1000, centennial to 1700, decadal to 1950, annual to 2025;
   cost and table width follow the steps, not the years. Limits are by scope, in one place (LIMITS).
   Usage: EdopsSpanGate.check('single'|'ring'|'buffer', fromYear, toYear) -> null, or {steps, limit, reason, message}. */
(function () {
  const STEPS = [];
  for (let y = -10000; y <= -1000; y += 1000) STEPS.push(y);
  for (let y = 0; y <= 1700; y += 100) STEPS.push(y);
  for (let y = 1710; y <= 1950; y += 10) STEPS.push(y);
  for (let y = 1951; y <= 2025; y += 1) STEPS.push(y);

  // single basin and ring: the HYDE table's width (about 14 columns fit the pane); buffer: delivery time, as a polity until measured
  const LIMITS = {
    single: { steps: 12, reason: 'wide' },
    ring:   { steps: 12, reason: 'wide' },
    buffer: { steps: 9,  reason: 'slow' },
  };

  const stepsIn = (from, to) => STEPS.filter(y => y >= from && y <= to).length;

  function check(scope, from, to) {
    const lim = LIMITS[scope];
    if (!lim || !Number.isFinite(from) || !Number.isFinite(to) || from > to) return null;
    const steps = stepsIn(from, to);
    if (steps <= lim.steps) return null;
    const why = lim.reason === 'wide' ? 'the HYDE table gets too wide to read' : 'the result can take a long time';
    return { steps, limit: lim.steps, reason: lim.reason,
             message: `This span has ${steps} HYDE steps; ${why} past ${lim.steps}. Try a shorter span.` };
  }

  // Band T time for an area, after the one-row-per-cell HYDE query: cells x (a cost per cell + a cost per step). Measured: about 2.1
  // microseconds a cell and step; per cell 13 (Northern Song) to 34 (China, a complex outline), 35 used. HYDE cells are about 73 km2
  // (Northern Song's ratio). A span with no step uses the nearest (one).
  const KM2_PER_CELL = 73, CEILING_S = 5, CELL_US = 35, STEP_US = 2.1;
  function estimateSeconds(areaKm2, from, to) {
    const cells = areaKm2 / KM2_PER_CELL;
    return cells * (CELL_US + STEP_US * Math.max(1, stepsIn(from, to))) * 1e-6;
  }
  function areaCheck(areaKm2, from, to) {
    if (!Number.isFinite(areaKm2) || !Number.isFinite(from) || !Number.isFinite(to)) return null;
    const seconds = estimateSeconds(areaKm2, from, to);
    if (seconds <= CEILING_S) return null;
    const when = seconds < 90 ? `${Math.round(seconds)} s` : `${Math.round(seconds / 60)} min`;
    return { seconds, message: `Band T for this slice would take about ${when}. Untick T to continue without it.` };
  }

  window.EdopsSpanGate = { check, stepsIn, estimateSeconds, areaCheck, ceiling: () => CEILING_S, steps: () => STEPS.slice(), limits: () => JSON.parse(JSON.stringify(LIMITS)) };
})();
