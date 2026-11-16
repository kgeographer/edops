/* Dashboard permalink codec: query string <-> state (version 1). No dependence on the page.
   Parameters mirror the API's names: lat, lon, name, scope (single_basin | basin_ring | buffer | polity), level, bands,
   from_year, to_year, radius_km, polity, year; plus v (version), member (a ring member's hybas_id) and view (the tab).
   Defaults: single_basin, Level 6, bands ABCDE (polities ABCDET), view profile (polities signature).
   parse(search) -> { state, errors, warnings }; state is null for a plain visit (no parameters of ours).
   Unknown parameters are ignored. build(state) -> query string without the "?". */
(function () {
  const VERSION = 1;
  const BANDS = 'ABCDET';
  const VIEWS = ['profile', 'map', 'signature', 'analysis', 'seasonality', 'context', 'similarity', 'atlas'];
  const SCOPES = ['single_basin', 'basin_ring', 'buffer', 'polity'];
  const KEYS = ['v', 'lat', 'lon', 'name', 'scope', 'level', 'bands', 'from_year', 'to_year', 'radius_km', 'member', 'polity', 'year', 'view'];
  const YEAR_MIN = -10000, YEAR_MAX = 2025;

  const clean = (s, max) => String(s).replace(/[\u0000-\u001f\u007f]+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
  const intOf = s => (/^-?\d+$/.test(String(s).trim()) ? parseInt(s, 10) : NaN);
  const numOf = s => (String(s).trim() !== '' && Number.isFinite(Number(s)) ? Number(s) : NaN);

  function parse(search) {
    const q = new URLSearchParams(search), errors = [], warnings = [];
    if (!KEYS.some(k => k !== 'v' && q.has(k))) return { state: null, errors, warnings };
    const get = k => (q.has(k) ? q.get(k) : null);

    if (get('v') !== null && intOf(get('v')) !== VERSION) {
      warnings.push(`This link is version "${clean(get('v'), 10)}"; this page reads version ${VERSION}, so some settings may be ignored.`);
    }
    const scope = get('scope') ?? (q.has('polity') ? 'polity' : 'single_basin');
    if (!SCOPES.includes(scope)) return { state: null, errors: [`scope must be one of ${SCOPES.join(', ')}.`], warnings };
    const kind = scope === 'polity' ? 'polity' : 'settlement';
    const st = { kind, scope };

    const level = get('level') === null ? 6 : intOf(get('level'));
    if (level !== 6 && level !== 8) errors.push('level must be 6 or 8.');
    st.level = level;

    let bands = get('bands') === null ? (kind === 'polity' ? 'ABCDET' : 'ABCDE') : String(get('bands')).toUpperCase();
    if (!bands || [...bands].some(c => !BANDS.includes(c))) { errors.push(`bands must be letters from ${BANDS}.`); bands = ''; }
    st.bands = [...new Set(bands)].sort((a, b) => BANDS.indexOf(a) - BANDS.indexOf(b)).join('');

    const view = get('view') ?? (kind === 'polity' ? 'signature' : 'profile');
    if (!VIEWS.includes(view)) errors.push(`view must be one of ${VIEWS.join(', ')}.`);
    st.view = view;

    if (kind === 'settlement') {
      const lat = get('lat') === null ? NaN : numOf(get('lat')), lon = get('lon') === null ? NaN : numOf(get('lon'));
      if (!(lat >= -90 && lat <= 90)) errors.push('lat is required, between -90 and 90.');
      if (!(lon >= -180 && lon <= 180)) errors.push('lon is required, between -180 and 180.');
      st.lat = lat; st.lon = lon;
      st.name = get('name') === null ? '' : clean(get('name'), 80);
      if (scope === 'buffer') {
        const r = get('radius_km') === null ? 100 : numOf(get('radius_km'));
        if (!(r >= 1 && r <= 2000)) errors.push('radius_km must be between 1 and 2000.');
        st.radiusKm = r;
      }
      if (scope === 'basin_ring' && get('member') !== null) {
        const m = intOf(get('member'));
        if (!(m > 0)) errors.push('member must be a basin id.');
        st.member = m;
      }
      if (st.bands.includes('T')) {
        const f = get('from_year') === null ? NaN : intOf(get('from_year')), t = get('to_year') === null ? NaN : intOf(get('to_year'));
        if (!(f >= YEAR_MIN && f <= YEAR_MAX && t >= YEAR_MIN && t <= YEAR_MAX && f <= t)) {
          errors.push(`Band T needs from_year and to_year, whole years between ${YEAR_MIN} and ${YEAR_MAX}, from_year not after to_year.`);
        }
        st.fromYear = f; st.toYear = t;
      }
    } else {
      const polity = get('polity') === null ? '' : clean(get('polity'), 100);
      if (!polity) errors.push('polity is required for scope=polity.');
      st.polity = polity;
      if (get('year') !== null) {
        const y = intOf(get('year'));
        if (!(y >= YEAR_MIN && y <= YEAR_MAX)) errors.push(`year must be a whole year between ${YEAR_MIN} and ${YEAR_MAX}.`);
        st.year = y;
      } else {
        st.year = null;
      }
    }
    return { state: errors.length ? null : st, errors, warnings };
  }

  function build(st) {
    const p = new URLSearchParams();
    p.set('v', String(VERSION));
    if (st.kind === 'polity') {
      p.set('scope', 'polity');
      p.set('polity', st.polity);
      if (st.year != null) p.set('year', String(st.year));
    } else {
      p.set('lat', String(Number(st.lat.toFixed(6))));
      p.set('lon', String(Number(st.lon.toFixed(6))));
      if (st.name) p.set('name', st.name);
      p.set('scope', st.scope);
      if (st.scope === 'buffer') p.set('radius_km', String(st.radiusKm));
      if (st.scope === 'basin_ring' && st.member != null) p.set('member', String(st.member));
      if (st.bands.includes('T')) { p.set('from_year', String(st.fromYear)); p.set('to_year', String(st.toYear)); }
    }
    p.set('level', String(st.level));
    p.set('bands', st.bands);
    p.set('view', st.view);
    return p.toString();
  }

  window.EdopsPermalink = { VERSION, parse, build };
})();
