/* Atlas tab of the Data Explorer: global climate-class distributions, place-independent. Moved from the Dashboard (WO-09).
   Paints the basin PMTiles by feature-state from the flat class dict (/api/explorer/climate-class); no query, no place. L6 + L8.
   Needs maplibregl with the pmtiles:// protocol registered, pmLightStyle() (pm_basemap.js) and the #ex-atlas-* elements and
   #ex-tab-atlas of explorer.html. While the tab is active the Explorer's variable selector and control strip give way to the
   Atlas text (#ex-left-atlas). */
(function () {
  const esc = s => String(s).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  const ATLAS_VIEWS = {
    mod:  { kind:'axis', axis:'modality', title:'Modality — all classes',
            blurb:'Every basin coloured by how its rainfall is spread through the year — from arid, through one or two wet seasons, to even year-round.' },
    pha:  { kind:'axis', axis:'phase', title:'Phase — all classes',
            blurb:'Every basin coloured by when its rain falls relative to warmth: with the warm season, against it (cool-season rain), weakly, or with no temperature cycle at all.' },
    twin: { kind:'hi', axis:'modality', match:'2-season', color:'#8E44AD', title:'Two wet seasons',
            blurb:'Basins with two distinct wet seasons a year. The tropical core (East Africa, Colombia, Sri Lanka, the Guinea coast, the maritime continent) is the classic bimodal “twin-rains”; the mid-latitude patches (SW USA, the Anatolia–Central Asia belt) are real spring-and-autumn bimodality — this class is the honest superset, not just the tropics.' },
    med:  { kind:'hi2', mod:'1-season', pha:'cool-wet', color:'#2166AC', title:'One wet season, cool-season rain',
            blurb:'A single wet season falling in the cool half of the year — the cool/cold-winter-wet family. The five classical Mediterranean regions are its mild-winter subset; it also includes the colder winter-rain belt through Iran and Central Asia.' },
  };
  let _atlasMap = null;
  let _atlasView = 'mod';
  let _atlasLevel = 6;
  let _atlasBasinLevel = null;
  const _atlasDicts = {};   // `${axis}${level}` -> {values, idToColor, idToCount, keyToId, categories, conventions}

  async function _atlasEnsureDicts(axis, level) {
    const k = `${axis}${level}`;
    if (_atlasDicts[k]) return _atlasDicts[k];
    const r = await fetch(`/api/explorer/climate-class?axis=${axis}&level=${level}`);
    if (!r.ok) throw new Error(`climate-class ${r.status}`);
    const data = await r.json();
    const idToColor = {}, idToCount = {}, keyToId = {};
    data.categories.forEach(c => { idToColor[c.id] = c.color; idToCount[c.id] = c.count; keyToId[c.key] = c.id; });
    _atlasDicts[k] = { values:data.values, idToColor, idToCount, keyToId,
                       categories:data.categories, conventions:data.meta.conventions };
    return _atlasDicts[k];
  }

  async function _atlasEnsureMap() {
    if (_atlasMap) { _atlasMap.resize(); return; }
    _atlasMap = new maplibregl.Map({
      container:'ex-atlas-map', center:[12, 25], zoom:1.1, attributionControl:true,
      style: pmLightStyle(),
    });
    await new Promise(res => _atlasMap.on('load', res));
  }

  function _atlasBasinLayer(level) {
    const sl = `basin0${level}`;
    if (_atlasBasinLevel === level && _atlasMap.getSource('atlas-basins')) return sl;
    ['atlas-basin-fill', 'atlas-basin-line'].forEach(id => { if (_atlasMap.getLayer(id)) _atlasMap.removeLayer(id); });
    if (_atlasMap.getSource('atlas-basins')) _atlasMap.removeSource('atlas-basins');
    _atlasMap.addSource('atlas-basins', { type:'vector', url:`pmtiles:///static/explorer/${sl}.pmtiles` });
    _atlasMap.addLayer({ id:'atlas-basin-fill', type:'fill', source:'atlas-basins', 'source-layer':sl,
      paint:{ 'fill-color':['coalesce', ['feature-state','fc'], 'transparent'], 'fill-opacity':0.85 } });
    _atlasMap.addLayer({ id:'atlas-basin-line', type:'line', source:'atlas-basins', 'source-layer':sl,
      paint:{ 'line-color':'rgba(90,90,90,0.12)', 'line-width':0.3 } });
    _atlasBasinLevel = level;
    return sl;
  }

  function _atlasLegendAxis(d) {
    document.getElementById('ex-atlas-legend').innerHTML = d.categories.filter(c => c.count > 0).map(c =>
      `<span class="d-inline-flex align-items-center gap-1"><span style="display:inline-block;width:14px;height:10px;background:${c.color};border:1px solid #ccc;border-radius:2px;"></span>`
      + `${esc(c.label)} <span class="text-muted">(${c.count.toLocaleString()})</span></span>`).join('');
  }
  function _atlasLegendHi(v, n) {
    document.getElementById('ex-atlas-legend').innerHTML =
      `<span class="d-inline-flex align-items-center gap-1"><span style="display:inline-block;width:14px;height:10px;background:${v.color};border:1px solid #ccc;border-radius:2px;"></span>`
      + `${esc(v.title)} <span class="text-muted">(${n.toLocaleString()} basins)</span></span>`
      + `<span class="text-muted" style="border-left:1px solid #dee2e6;padding-left:0.6rem;">all other basins in grey</span>`;
  }

  function _atlasRenderInfo(v, conventions) {
    const el = document.getElementById('ex-atlas-info');
    if (!el) return;
    el.innerHTML = `<p class="mb-2"><strong>${esc(v.title)}</strong></p>`
      + `<p class="mb-2">${esc(v.blurb)}</p>`
      + (conventions ? `<p class="text-muted mb-0" style="font-size:0.72rem;">${esc(conventions)}</p>` : '');
  }

  async function renderAtlas() {
    try {
      await _atlasEnsureMap();
      const sl = _atlasBasinLayer(_atlasLevel);
      const v  = ATLAS_VIEWS[_atlasView];
      document.getElementById('ex-atlas-title').textContent = v.title;
      _atlasMap.removeFeatureState({ source:'atlas-basins', sourceLayer:sl });
      let conventions = '';

      if (v.kind === 'axis') {
        const d = await _atlasEnsureDicts(v.axis, _atlasLevel);
        conventions = d.conventions;
        for (const [id, cat] of Object.entries(d.values))
          _atlasMap.setFeatureState({ source:'atlas-basins', sourceLayer:sl, id:Number(id) }, { fc: d.idToColor[cat] || '#ccc' });
        _atlasLegendAxis(d);

      } else if (v.kind === 'hi') {
        const d = await _atlasEnsureDicts(v.axis, _atlasLevel);
        conventions = d.conventions;
        const matchId = d.keyToId[v.match]; let n = 0;
        for (const [id, cat] of Object.entries(d.values)) {
          const hit = (cat === matchId); if (hit) n++;
          _atlasMap.setFeatureState({ source:'atlas-basins', sourceLayer:sl, id:Number(id) }, { fc: hit ? v.color : '#e9e9e9' });
        }
        _atlasLegendHi(v, n);

      } else if (v.kind === 'hi2') {
        const dm = await _atlasEnsureDicts('modality', _atlasLevel);
        const dp = await _atlasEnsureDicts('phase', _atlasLevel);
        conventions = dm.conventions;
        const modId = dm.keyToId[v.mod], phaId = dp.keyToId[v.pha]; let n = 0;
        for (const [id, cat] of Object.entries(dm.values)) {
          const hit = (cat === modId && dp.values[id] === phaId); if (hit) n++;
          _atlasMap.setFeatureState({ source:'atlas-basins', sourceLayer:sl, id:Number(id) }, { fc: hit ? v.color : '#e9e9e9' });
        }
        _atlasLegendHi(v, n);
      }
      _atlasRenderInfo(v, conventions);
    } catch (err) {
      console.error('[atlas]', err);
      document.getElementById('ex-atlas-legend').innerHTML =
        '<span class="text-danger">Could not load climate classes.</span>';
    }
  }

  const tabBtn = document.getElementById('ex-tab-atlas');
  if (!tabBtn) return;
  const left = document.getElementById('ex-left');
  const controls = document.getElementById('ex-controls');
  const setAtlasChrome = on => {
    const hide = (el, yes) => yes ? el.style.setProperty('display', 'none', 'important') : el.style.removeProperty('display');   // !important beats d-flex
    [...left.children].forEach(c => { if (c.id !== 'ex-left-atlas') hide(c, on); });
    document.getElementById('ex-left-atlas').classList.toggle('d-none', !on);
    if (controls) hide(controls, on);
  };
  document.getElementById('ex-atlas-view').addEventListener('change', function () { _atlasView = this.value; renderAtlas(); });
  document.getElementById('ex-atlas-level').addEventListener('change', function () { _atlasLevel = parseInt(this.value, 10); renderAtlas(); });
  tabBtn.addEventListener('shown.bs.tab', () => { setAtlasChrome(true); renderAtlas(); });
  tabBtn.addEventListener('hide.bs.tab', () => setAtlasChrome(false));
})();
