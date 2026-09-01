// Minimal Positron-style basemap from the self-hosted Protomaps vector tiles
// (app/static/basemaps/protomaps-light.pmtiles, z0-9). Land / water / admin
// bounds / sparse labels only -- a quiet base under choropleth painting.
// Shared by sandbox.html (Similarity / Context panel maps) and workbench.html
// (African Regions tab). Needs the pmtiles:// protocol registered on maplibregl
// and the .pmtiles asset served at /static/basemaps/.
function pmLightStyle() {
  const NAME = ['coalesce', ['get', 'name:en'], ['get', 'name']];
  const FONT = ['Noto Sans Regular'];
  const HALO = '#f6f6f4';
  return {
    version: 8,
    glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    sources: {
      pm: {
        type: 'vector',
        url: 'pmtiles:///static/basemaps/protomaps-light.pmtiles',
        attribution: '<a href="https://protomaps.com">Protomaps</a> &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
      },
    },
    layers: [
      { id: 'pm-bg', type: 'background', paint: { 'background-color': HALO } },
      { id: 'pm-earth', type: 'fill', source: 'pm', 'source-layer': 'earth',
        filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': '#eceae6' } },
      { id: 'pm-water', type: 'fill', source: 'pm', 'source-layer': 'water',
        filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': '#dde4e7' } },
      { id: 'pm-boundary-region', type: 'line', source: 'pm', 'source-layer': 'boundaries',
        filter: ['>', ['get', 'kind_detail'], 2],
        paint: { 'line-color': '#d2d2d2', 'line-width': 0.5, 'line-dasharray': [2, 2] } },
      { id: 'pm-boundary-country', type: 'line', source: 'pm', 'source-layer': 'boundaries',
        filter: ['<=', ['get', 'kind_detail'], 2],
        paint: { 'line-color': '#bcbcbc', 'line-width': 0.7 } },
      { id: 'pm-label-country', type: 'symbol', source: 'pm', 'source-layer': 'places',
        filter: ['==', ['get', 'kind'], 'country'],
        layout: { 'text-field': NAME, 'text-font': FONT, 'text-transform': 'uppercase',
          'text-letter-spacing': 0.08, 'text-max-width': 6,
          'text-size': ['interpolate', ['linear'], ['zoom'], 2, 9, 6, 13] },
        paint: { 'text-color': '#6e6e70', 'text-halo-color': HALO, 'text-halo-width': 1.4 } },
      { id: 'pm-label-region', type: 'symbol', source: 'pm', 'source-layer': 'places',
        filter: ['==', ['get', 'kind'], 'region'], minzoom: 3,
        layout: { 'text-field': NAME, 'text-font': FONT, 'text-max-width': 7,
          'text-size': ['interpolate', ['linear'], ['zoom'], 3, 9, 7, 12] },
        paint: { 'text-color': '#8a8a8c', 'text-halo-color': HALO, 'text-halo-width': 1.1 } },
      { id: 'pm-label-city', type: 'symbol', source: 'pm', 'source-layer': 'places',
        filter: ['all', ['==', ['get', 'kind'], 'locality'],
          ['>=', ['get', 'population_rank'], ['step', ['zoom'], 12, 4, 10, 7, 9]]],
        layout: { 'text-field': NAME, 'text-font': FONT, 'text-max-width': 7,
          'text-size': ['interpolate', ['linear'], ['zoom'], 3, 10, 8, 12] },
        paint: { 'text-color': '#8a8a8c', 'text-halo-color': HALO, 'text-halo-width': 1.1 } },
    ],
  };
}
