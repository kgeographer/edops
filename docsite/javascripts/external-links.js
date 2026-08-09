// Opens in-content links to other domains in a new tab; internal/relative links unaffected.
(function () {
  function markExternalLinks() {
    document.querySelectorAll('.md-typeset a[href^="http"]').forEach(function (a) {
      if (a.hostname !== location.hostname) {
        a.target = '_blank';
        a.rel = 'noopener';
      }
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markExternalLinks);
  } else {
    markExternalLinks();
  }
})();
