// When the docs are loaded inside an iframe (the app's Documentation / Guide modals),
// strip Material's page branding from the header -- but keep .md-search, which is the
// one thing the modal can't otherwise offer. Never touches the standalone /docs site.
(function () {
  if (window.self === window.top) return;
  var header = document.querySelector('.md-header');
  if (!header) return;
  ['.md-header__button.md-logo', '.md-header__title', '.md-header__source'].forEach(function (sel) {
    var el = header.querySelector(sel);
    if (el) el.style.display = 'none';
  });
})();
